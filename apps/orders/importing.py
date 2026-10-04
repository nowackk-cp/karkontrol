"""Dosya girdisini doğrular; tüm satırları tek transaction içinde kaydeder."""

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO, StringIO
from pathlib import Path
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile, ZipFile

from defusedxml.common import DefusedXmlException
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from apps.stores.models import Store

from .models import ImportBatch, OrderLine

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_EXPANDED_BYTES = 25 * 1024 * 1024
MAX_ROWS = 5000
REQUIRED_COLUMNS = (
    "siparis_no",
    "satir_no",
    "tarih",
    "urun_adi",
    "urun_kodu",
    "adet",
    "birim_fiyat_kdv_dahil",
    "kdv_orani",
    "birim_maliyet_kdv_haric",
)
OPTIONAL_COLUMNS = (
    "komisyon_orani",
    "satici_indirimi",
    "pazaryeri_kuponu",
    "iade_adet",
    "para_birimi",
    "desi",
    "agirlik_kg",
    "maliyet_kdv_orani",
    "doviz_kuru",
)


class ImportValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ImportResult:
    created: int
    skipped: int
    repeated_file: bool = False


def _text(value):
    return "" if value is None else str(value).strip()


def _decimal(value, label):
    # Excel numeric values cross the adapter as text; money is always Decimal
    # before validation, storage or arithmetic. Thousands separators are forbidden.
    text = _text(value)
    if not re.fullmatch(r"[0-9]+(?:[.,][0-9]{1,2})?", text):
        raise ImportValidationError(f"{label}: negatif olmayan, en fazla iki ondalıklı sayı girin.")
    return Decimal(text.replace(",", "."))


def _integer(value, label):
    text = _text(value)
    if len(text) > 10 or not re.fullmatch(r"[0-9]+", text):
        raise ImportValidationError(
            f"{label}: en fazla 10 basamaklı negatif olmayan tam sayı girin."
        )
    value = int(text)
    if value > 2_147_483_647:
        raise ImportValidationError(f"{label}: en fazla 2147483647 olabilir.")
    return value


def _date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    for pattern in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(_text(value), pattern).date()
        except ValueError:
            continue
    raise ImportValidationError("tarih: YYYY-AA-GG veya GG.AA.YYYY biçimini kullanın.")


def _csv_rows(content):
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ImportValidationError("CSV dosyasını UTF-8 olarak kaydedin.") from exc
    delimiter = ";" if ";" in text.partition("\n")[0] else ","
    try:
        yield from csv.reader(StringIO(text), delimiter=delimiter, strict=True)
    except csv.Error as exc:
        raise ImportValidationError(
            "CSV yapısı geçersiz; ayraçları ve tırnakları kontrol edin."
        ) from exc


def _xlsx_rows(content):
    try:
        with ZipFile(BytesIO(content)) as archive:
            entries = archive.infolist()
            if len(entries) > 200 or sum(item.file_size for item in entries) > MAX_EXPANDED_BYTES:
                raise ImportValidationError("Excel dosyasının açılmış boyutu sınırı aşıyor.")
        workbook = load_workbook(
            BytesIO(content), read_only=True, data_only=False, keep_links=False
        )
        try:
            if len(workbook.worksheets) != 1:
                raise ImportValidationError("Excel dosyası tek çalışma sayfası içermeli.")
            sheet = workbook.worksheets[0]
            # Ignore untrusted worksheet dimension metadata; bound actual rows/columns below.
            sheet.reset_dimensions()
            for row in sheet.iter_rows():
                if len(row) > len(REQUIRED_COLUMNS) + len(OPTIONAL_COLUMNS):
                    raise ImportValidationError("Excel dosyasında fazla sütun var.")
                if any(cell.data_type == "f" for cell in row):
                    raise ImportValidationError(
                        "Formül yerine hesaplanmış hücre değerlerini aktarın."
                    )
                yield [cell.value for cell in row]
        finally:
            workbook.close()
    except (
        BadZipFile,
        InvalidFileException,
        ParseError,
        DefusedXmlException,
        KeyError,
        ValueError,
        TypeError,
        OSError,
    ) as exc:
        if isinstance(exc, ImportValidationError):
            raise
        raise ImportValidationError(
            "Excel dosyası okunamadı; geçerli bir .xlsx dosyası kullanın."
        ) from exc


def _parse(content, extension, store):
    rows = iter(_csv_rows(content) if extension == ".csv" else _xlsx_rows(content))
    try:
        headers = [_text(value) for value in next(rows)]
    except StopIteration as exc:
        raise ImportValidationError("Dosya boş.") from exc
    if len(headers) != len(set(headers)):
        raise ImportValidationError("Sütun adları tekrar edemez.")
    missing = set(REQUIRED_COLUMNS) - set(headers)
    unknown = set(headers) - set(REQUIRED_COLUMNS + OPTIONAL_COLUMNS)
    if missing:
        raise ImportValidationError("Eksik sütunlar: " + ", ".join(sorted(missing)))
    if unknown:
        raise ImportValidationError("Bilinmeyen sütunlar: " + ", ".join(sorted(unknown)))

    lines = []
    identities = set()
    for index, values in enumerate(rows, start=2):
        if index > MAX_ROWS + 1:
            raise ImportValidationError(f"Dosya en fazla {MAX_ROWS} veri satırı içerebilir.")
        if all(not _text(value) for value in values):
            continue
        if len(values) > len(headers):
            raise ImportValidationError(f"Satır {index}: başlıktan fazla hücre var.")
        values = list(values) + [None] * (len(headers) - len(values))
        row = dict(zip(headers, values, strict=True))
        try:
            currency = _text(row.get("para_birimi")) or "TRY"
            rate = _text(row.get("doviz_kuru")) or "1"
            if currency not in ("TRY", "USD", "EUR") or (
                currency != "TRY" and store.marketplace != Store.Marketplace.AMAZON
            ):
                raise ImportValidationError("Bu mağazada para birimi desteklenmiyor.")
            if currency != "TRY" and not _text(row.get("doviz_kuru")):
                raise ImportValidationError("Yabancı para siparişlerinde doviz_kuru zorunlu.")
            if not re.fullmatch(r"[0-9]{1,6}(?:[.,][0-9]{1,6})?", rate):
                raise ImportValidationError(
                    "doviz_kuru: en fazla altı ondalıklı pozitif sayı girin."
                )
            line = OrderLine(
                store=store,
                order_number=_text(row["siparis_no"]),
                line_number=_integer(row["satir_no"], "satir_no"),
                order_date=_date(row["tarih"]),
                product_name=_text(row["urun_adi"]),
                sku=_text(row["urun_kodu"]),
                quantity=_integer(row["adet"], "adet"),
                unit_price_gross=_decimal(row["birim_fiyat_kdv_dahil"], "birim_fiyat_kdv_dahil"),
                unit_cost_net=_decimal(row["birim_maliyet_kdv_haric"], "birim_maliyet_kdv_haric"),
                vat_percent=_decimal(row["kdv_orani"], "kdv_orani"),
                commission_percent=(
                    _decimal(row["komisyon_orani"], "komisyon_orani")
                    if _text(row.get("komisyon_orani"))
                    else store.commission_percent
                ),
                seller_discount=_decimal(row.get("satici_indirimi") or "0", "satici_indirimi"),
                platform_coupon=_decimal(row.get("pazaryeri_kuponu") or "0", "pazaryeri_kuponu"),
                returned_quantity=_integer(row.get("iade_adet") or "0", "iade_adet"),
                currency=currency,
                exchange_rate=Decimal(rate.replace(",", ".")),
                desi=_decimal(row.get("desi") or "0", "desi"),
                weight_kg=_decimal(row.get("agirlik_kg") or "0", "agirlik_kg"),
                cost_vat_percent=_decimal(
                    row.get("maliyet_kdv_orani") or "20", "maliyet_kdv_orani"
                ),
            )
            line.full_clean(validate_unique=False, validate_constraints=False)
            identity = (line.order_number, line.line_number)
            if identity in identities:
                raise ImportValidationError(
                    "Aynı sipariş satırı dosyada birden fazla kez bulunuyor."
                )
            identities.add(identity)
            lines.append(line)
        except (ImportValidationError, ValidationError) as exc:
            detail = "; ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc)
            raise ImportValidationError(f"Satır {index}: {detail}") from exc
    if not lines:
        raise ImportValidationError("Dosyada sipariş satırı yok.")
    return lines


def import_orders(*, user, store_pk, upload):
    store = get_object_or_404(Store, pk=store_pk, owner=user)
    extension = Path(upload.name).suffix.lower()
    if extension not in (".csv", ".xlsx"):
        raise ImportValidationError("Yalnızca .csv ve .xlsx dosyaları yüklenebilir.")
    content = upload.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise ImportValidationError("Dosya boyutu en fazla 5 MB olabilir.")
    lines = _parse(content, extension, store)
    digest = hashlib.sha256(content).hexdigest()
    with transaction.atomic():
        batch, created = ImportBatch.objects.get_or_create(store=store, digest=digest)
        if not created:
            return ImportResult(0, len(lines), repeated_file=True)
        created_count = skipped_count = 0
        new_orders = set()
        for line in lines:
            defaults = {
                field.name: getattr(line, field.name)
                for field in OrderLine._meta.fields
                if field.name not in ("id", "store", "order_number", "line_number")
            }
            existing, is_new = OrderLine.objects.get_or_create(
                store=store,
                order_number=line.order_number,
                line_number=line.line_number,
                defaults=defaults,
            )
            if is_new:
                created_count += 1
                new_orders.add(line.order_number)
            elif any(getattr(existing, name) != value for name, value in defaults.items()):
                raise ImportValidationError(
                    f"{line.order_number} / {line.line_number}: "
                    "mevcut kayıtla çelişiyor; dosya aktarılmadı."
                )
            else:
                skipped_count += 1
        from apps.billing.services import check_import_limit
        from apps.reports.services import check_report_bounds, recalculate_order

        check_import_limit(user)
        try:
            for number in new_orders:
                recalculate_order(store, number, enforce_totals=False)
            check_report_bounds(store)
        except ValueError as exc:
            raise ImportValidationError(str(exc)) from exc
        batch.created_lines = created_count
        batch.skipped_lines = skipped_count
        batch.save(update_fields=["created_lines", "skipped_lines"])
    return ImportResult(created_count, skipped_count)
