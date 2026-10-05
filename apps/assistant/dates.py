"""Resolve the supported report periods without interpreting money as dates."""

import calendar
import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from django.utils import timezone

MONTH_NAMES = (
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)


def normalize_question(text):
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text.casefold().replace("ı", "i"))
        if not unicodedata.combining(char)
    )


@dataclass(frozen=True)
class Period:
    year: int | None = None
    month: int | None = None
    error: str = ""

    @property
    def filters(self):
        if self.year is None:
            return {}
        return {
            "start": date(self.year, self.month or 1, 1),
            "end": date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])
            if self.month
            else date(self.year, 12, 31),
        }

    @property
    def label(self):
        if self.month and self.year:
            return f"{MONTH_NAMES[self.month - 1]} {self.year}"
        return f"{self.year} yılı" if self.year else "Tüm dönemler"


def resolve_period(question, *, today=None):
    text = normalize_question(question)
    pairs = set()
    for match in re.finditer(r"\b(0?[1-9]|1[0-2])/(19\d{2}|20\d{2}|21\d{2})\b", text):
        pairs.add((int(match[2]), int(match[1])))
    for match in re.finditer(r"\b(19\d{2}|20\d{2}|21\d{2})-(0?[1-9]|1[0-2])\b", text):
        pairs.add((int(match[1]), int(match[2])))
    years = {
        int(match[1])
        for match in re.finditer(r"\b(19\d{2}|20\d{2}|21\d{2})\b", text)
        if not re.match(
            r"(?:[.,]\d+)?\s*(?:tl\b|try\b|usd\b|eur\b|lira\b|dolar\b|euro\b|₺|\$|€|adet\b)",
            text[match.end() :],
        )
    }
    months = set()
    for number, name in enumerate(MONTH_NAMES, 1):
        normalized = normalize_question(name)
        # Aralıkta means "in a range" as well: require the unambiguous month token.
        endings = "" if number == 12 else r"(?:[\x27’]?(?:da|de|ta|te))?"
        if re.search(r"\b" + normalized + endings + r"\b", text):
            months.add(number)
    for year, month in pairs:
        years.add(year)
        months.add(month)
    relative = [
        phrase
        for phrase in ("gecen ay", "bu ay", "gecen yil", "bu yil")
        if re.search(r"\b" + phrase + r"\b", text)
    ]
    if len(years) > 1 or len(months) > 1 or len(pairs) > 1 or len(relative) > 1:
        return Period(error="Bir dönem seçin; birden fazla yıl veya ayı birlikte inceleyemiyorum.")
    if relative:
        if years or months:
            return Period(error="Göreli tarih ile açık tarih birlikte verilmiş; bir dönem seçin.")
        current = today or timezone.localdate()
        phrase = relative[0]
        if phrase == "gecen ay":
            return Period(current.year - (current.month == 1), current.month - 1 or 12)
        if phrase == "bu ay":
            return Period(current.year, current.month)
        return Period(current.year - (phrase == "gecen yil"))
    year = next(iter(years), None)
    month = next(iter(months), None)
    if year is not None and not 1990 <= year <= 2100:
        return Period(error="1990–2100 arasında açık bir rapor yılı yazın.")
    if re.search(r"\b(?:\d{2}/\d{4}|\d{4}-\d{2})\b", text) and not pairs:
        return Period(error="Geçerli ay/yıl biçimi kullanın: 09/2026 veya 2026-09.")
    return Period(year, month)
