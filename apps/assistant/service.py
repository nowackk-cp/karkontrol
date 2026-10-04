"""Anahtarsız, araçlara dayalı deterministik asistan. LLM başarısı iddiası yoktur."""

import calendar
import re
from datetime import date

from django.shortcuts import get_object_or_404

from apps.reports.templatetags.money import tl
from apps.stores.models import Store

from .tools import RULES, explain_rule, product_profit, profit_summary, return_statistics

MONTHS = {
    "ocak": 1,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "ağustos": 8,
    "eylül": 9,
    "ekim": 10,
    "kasım": 11,
    "aralık": 12,
}
NUMBERS = re.compile(r"(?<!\w)-?\d+(?:[.,]\d+)*(?!\w)")


def guardrail(answer, allowed_numbers):
    """Her sayısal token, araçtan gelen beyaz listedeki değerle tam eşleşmeli."""
    return set(NUMBERS.findall(answer)) <= set(allowed_numbers)


def _render(data):
    allowed = set()

    def cash(cents):
        value = tl(cents)
        allowed.update(NUMBERS.findall(value))
        return value

    def count(value):
        allowed.add(str(value))
        return str(value)

    if data["kind"] == "rule":
        answer = data["text"]
    elif data["kind"] == "summary":
        if not data["count"]:
            answer = "Bu aralıkta veri yok. Dosya yükleyin veya tarih aralığını değiştirin."
        else:
            amounts = data["amounts"]
            answer = (
                f"{count(data['count'])} satır için net kâr {cash(amounts['profit'])}; "
                f"hakediş {cash(amounts['payout'])}; net satış {cash(amounts['net_sales'])}."
            )
    elif data["kind"] == "products":
        if not data["products"]:
            answer = "Bu aralıkta veri yok."
        else:
            # Product identifiers are untrusted data; never execute or quote instructions as advice.
            labels = []
            for product in data["products"]:
                label = product["sku"]
                allowed.update(NUMBERS.findall(label))
                labels.append(f"{label}: {cash(product['profit'])}")
            answer = "Net kâra göre ürünler: " + "; ".join(labels) + "."
    else:
        answer = (
            f"Toplam {count(data['quantity'])} adet içinde {count(data['returned'])} adet iade var."
        )
    return answer, allowed


def ask(*, user, store_pk, question):
    # Security boundary is enforced before intent selection; identifiers never come from a model.
    store = get_object_or_404(Store, pk=store_pk, owner=user)
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        return {"answer": "Kısa bir soru yazın.", "status": "clarify", "tool": None}
    text = question.casefold().replace("i̇", "i")
    if any(
        word in text
        for word in (
            "başka",
            "diğer satıcı",
            "ignore",
            "talimat",
            "sistem prompt",
            "şifre",
            "secret",
            "sql",
            "drop",
            "api anahtar",
        )
    ):
        return {
            "answer": (
                "Bu isteği yerine getiremiyorum. "
                "Yalnız seçili mağazanızın raporlarına erişebilirim."
            ),
            "status": "refused",
            "tool": None,
        }
    filters = {}
    month = next((value for name, value in MONTHS.items() if name in text), None)
    year_match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", text)
    if month and not year_match:
        return {
            "answer": "Hangi yıl için bu ayı inceleyelim? Örneğin ay adıyla birlikte yılı yazın.",
            "status": "clarify",
            "tool": None,
        }
    if year_match:
        year = int(year_match.group())
        filters = {
            "start": date(year, month or 1, 1),
            "end": date(year, month, calendar.monthrange(year, month)[1])
            if month
            else date(year, 12, 31),
        }
    if any(word in text for word in ("nasıl", "nedir", "neden", "etkiler", "kural")):
        topic = next((name for name in RULES if name in text), None)
        if topic:
            data = explain_rule(topic)
        elif "kâr" in text or "kar" in text:
            data = profit_summary(store, filters)
        else:
            return {
                "answer": (
                    "Net kâr, hakediş, ürün kârlılığı, iade veya hesap "
                    "kuralları hakkında sorabilirsiniz."
                ),
                "status": "unsupported",
                "tool": None,
            }
    elif any(word in text for word in ("ürün", "sıralama", "en kârlı", "en karli")):
        data = product_profit(store, filters)
    elif "iade" in text:
        data = return_statistics(store, filters)
    elif any(word in text for word in ("kâr", "kar", "hakediş", "satış", "özet")):
        data = profit_summary(store, filters)
    else:
        return {
            "answer": (
                "Bu konu kapsamım dışında. Mağazanızın finans raporları hakkında sorabilirsiniz."
            ),
            "status": "unsupported",
            "tool": None,
        }
    answer, allowed = _render(data)
    if not guardrail(answer, allowed):
        return {
            "answer": "Yanıtın sayısal doğrulaması başarısız oldu.",
            "status": "blocked",
            "tool": data,
        }
    return {"answer": answer, "status": "ok", "tool": data, "allowed_numbers": sorted(allowed)}
