from django.db.models import Sum

from apps.reports.services import filtered_lines, summary


def profit_summary(store, filters):
    lines = filtered_lines(store, filters)
    return {"kind": "summary", "count": lines.count(), "amounts": summary(lines)}


def product_profit(store, filters):
    rows = (
        filtered_lines(store, filters)
        .values("sku")
        .annotate(
            profit=Sum("financial__profit"),
            sales=Sum("financial__net_sales"),
        )
        .order_by("-profit", "sku")[:3]
    )
    return {"kind": "products", "products": list(rows)}


def return_statistics(store, filters):
    totals = filtered_lines(store, filters).aggregate(
        quantity=Sum("quantity"),
        returned=Sum("returned_quantity"),
    )
    return {"kind": "returns", **{name: value or 0 for name, value in totals.items()}}


RULES = {
    "stopaj": "Stopaj net satış üzerinden hesaplanır; hakedişi azaltır. Kâr gideri değildir.",
    "kupon": "Platform kuponunu platform karşılar. Satıcı indirimi satıcının gelirini azaltır.",
    "iade": "İade edilen stok maliyeti geri alınır. Gidiş kargosu kalır ve dönüş kargosu eklenir.",
    "kdv": "Kâr net tutarlarla hesaplanır. Hakedişte platform ücretlerinin KDV'si de düşülür.",
    "kargo": "Kargo sipariş başına uygulanır ve satırlara en büyük kalan yöntemiyle dağıtılır.",
    "kur": "Sipariş kuru sabittir. Yabancı para satışları kaydedilmiş kurla TRY'ye çevrilir.",
}


def explain_rule(topic):
    return {"kind": "rule", "text": RULES[topic], "source": "KURALLAR_v1.md / KURALLAR_v2.md"}
