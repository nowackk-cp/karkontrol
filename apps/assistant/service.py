"""Anahtarsız, araçlara dayalı deterministik asistan. LLM başarısı iddiası yoktur."""

import re

from django.shortcuts import get_object_or_404

from apps.reports.templatetags.money import tl
from apps.stores.models import Store

from .dates import normalize_question, resolve_period
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


def unsafe_question(question):
    text = normalize_question(question)
    return bool(
        re.search(
            r"\b(?:baska|rakip|ignore|talimat|sifre|secret|sql|drop)\b"
            r"|\bdiger\s+(?:satici|magaza)|\bsistem\s+prompt|\bapi\s+anahtar"
            r"|\b(?:tum|butun)\s+(?:satici|magaza)",
            text,
        )
    )


def unsupported_amount_filter(question):
    return bool(
        re.search(
            r"\d\s*(?:tl\b|try\b|usd\b|eur\b|lira\b|dolar\b|euro\b|₺|\$|€)",
            normalize_question(question),
        )
    )


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
    if data.get("period"):
        label = data["period"]["label"]
        allowed.update(NUMBERS.findall(label))
        answer = f"{label}: {answer}"
    return answer, allowed


def ask(*, user, store_pk, question):
    # Security boundary is enforced before intent selection; identifiers never come from a model.
    store = get_object_or_404(Store, pk=store_pk, owner=user)
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        return {"answer": "Kısa bir soru yazın.", "status": "clarify", "tool": None}
    text = normalize_question(question)
    if unsafe_question(question):
        return {
            "answer": (
                "Bu isteği yerine getiremiyorum. "
                "Yalnız seçili mağazanızın raporlarına erişebilirim."
            ),
            "status": "refused",
            "tool": None,
        }
    period = resolve_period(question)
    if period.error:
        return {"answer": period.error, "status": "clarify", "tool": None}
    if unsupported_amount_filter(question):
        return {
            "answer": "Tutar eşiği filtresi desteklenmiyor; kâr raporunu inceleyin.",
            "status": "unsupported",
            "tool": None,
        }
    if period.month and not period.year:
        return {
            "answer": "Hangi yıl için bu ayı inceleyelim? Örneğin ay adıyla birlikte yılı yazın.",
            "status": "clarify",
            "tool": None,
        }
    filters = period.filters
    profit_intent = bool(re.search(r"\bkar(?:im|i|in|imiz|iniz|larim|a|dan)?\b", text))
    if any(word in text for word in ("nasil", "nedir", "neden", "etkiler", "kural")):
        topic = next((name for name in RULES if re.search(r"\b" + name + r"\b", text)), None)
        if topic:
            data = explain_rule(topic)
        elif profit_intent:
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
    elif any(word in text for word in ("urun", "siralama", "en karli")):
        data = product_profit(store, filters)
    elif "iade" in text:
        data = return_statistics(store, filters)
    elif profit_intent or any(word in text for word in ("hakedis", "satis", "ozet")):
        data = profit_summary(store, filters)
    else:
        return {
            "answer": (
                "Bu konu kapsamım dışında. Mağazanızın finans raporları hakkında sorabilirsiniz."
            ),
            "status": "unsupported",
            "tool": None,
        }
    if data["kind"] != "rule":
        data["period"] = {**{k: v.isoformat() for k, v in filters.items()}, "label": period.label}
    answer, allowed = _render(data)
    if not guardrail(answer, allowed):
        return {
            "answer": "Yanıtın sayısal doğrulaması başarısız oldu.",
            "status": "blocked",
            "tool": data,
        }
    return {"answer": answer, "status": "ok", "tool": data, "allowed_numbers": sorted(allowed)}
