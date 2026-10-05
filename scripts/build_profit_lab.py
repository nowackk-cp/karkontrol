"""Kâr Laboratuvarı verisini ve README grafiğini gerçek motor çıktısından üretir.

Tarayıcı tarafı para hesabı yapmaz; yalnız bu dosyanın yazdığı kuruş değerlerini gösterir.
`tests/unit/test_profit_lab.py` kayıtlı dosyaların motorla aynı kaldığını denetler.
"""

import argparse
import json
from decimal import Decimal
from pathlib import Path

from engine.profit import VERSION, LineInput, calculate_order

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs" / "lab" / "data.json"
SVG_PATH = ROOT / "docs" / "assets" / "showcase" / "profit-cliff.svg"

COMMISSIONS = ("10", "15", "20", "25")
COSTS = ("80.00", "120.00", "200.00")
# 1 TL adımlı ızgara ve barem eşiklerinin bir kuruş üstü.
PRICES = sorted({Decimal(tl) for tl in range(100, 801)} | {Decimal("300.01"), Decimal("600.01")})
FIELDS = (
    "net_sales",
    "commission",
    "shipping",
    "service",
    "cost",
    "withholding",
    "profit",
    "payout",
)


def cents(value: Decimal) -> int:
    return int(value * 100)


def scenario(commission: str, cost: str) -> dict:
    columns = {field: [] for field in FIELDS}
    for price in PRICES:
        (result,) = calculate_order(
            [
                LineInput(
                    line_number=1,
                    quantity=1,
                    unit_price_gross=price.quantize(Decimal("0.01")),
                    unit_cost_net=Decimal(cost),
                    vat_percent=Decimal("20"),
                    commission_percent=Decimal(commission),
                )
            ]
        )
        for field in FIELDS:
            columns[field].append(cents(getattr(result, field)))
    return columns


def build_data() -> dict:
    return {
        "engine": VERSION,
        "note": "engine/profit.py çıktısı; tutarlar kuruş cinsinden tamsayıdır.",
        "inputs": {"quantity": 1, "vat_percent": 20, "desi": 1},
        "prices": [cents(price) for price in PRICES],
        "fields": list(FIELDS),
        "scenarios": {
            f"{commission}|{cost}": scenario(commission, cost)
            for commission in COMMISSIONS
            for cost in COSTS
        },
    }


def tl(value: int) -> str:
    sign = "−" if value < 0 else ""
    whole, frac = divmod(abs(value), 100)
    return f"{sign}{whole:,}".replace(",", ".") + f",{frac:02d} ₺"


def build_svg(data: dict) -> str:
    prices = data["prices"]
    profit = data["scenarios"]["20|120.00"]["profit"]
    width, height, left, right, top, bottom = 900, 400, 70, 30, 70, 50
    low, high = min(profit), max(profit)
    span = high - low

    def x(price):
        return left + (price - prices[0]) / (prices[-1] - prices[0]) * (width - left - right)

    def y(value):
        return top + (high - value) / span * (height - top - bottom)

    points = " ".join(f"{x(p):.1f},{y(v):.1f}" for p, v in zip(prices, profit, strict=True))
    marks = []
    for edge in (30000, 60000):
        before, after = prices.index(edge), prices.index(edge + 1)
        drop = profit[before] - profit[after]
        cx, cy = x(edge), y(profit[after])
        # Sağ kenardaki işaretin etiketi taşmasın diye sola hizalanır.
        tx, anchor, dy = (cx + 12, "start", 26) if edge == 30000 else (cx - 14, "end", -58)
        marks.append(
            f'<g class="mark" style="animation-delay:{2.2 + len(marks) * 0.5}s">'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" class="pulse"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="#ff5d73"/>'
            f'<text x="{tx:.1f}" y="{cy + dy:.1f}" class="lbl" text-anchor="{anchor}">'
            f"{tl(edge)} → {tl(edge + 1)}</text>"
            f'<text x="{tx:.1f}" y="{cy + dy + 20:.1f}" class="drop" text-anchor="{anchor}">'
            f"+0,01 ₺ fiyat = −{tl(drop)}"
            f" kâr</text></g>"
        )
    grid = []
    for value in range(0, high + 1, 10000):
        grid.append(
            f'<line x1="{left}" x2="{width - right}" y1="{y(value):.1f}" y2="{y(value):.1f}"'
            f' class="grid"/><text x="{left - 10}" y="{y(value) + 4:.1f}" class="axis"'
            f' text-anchor="end">{value // 100}</text>'
        )
    for price in range(10000, 80001, 10000):
        grid.append(
            f'<text x="{x(price):.1f}" y="{height - bottom + 22}" class="axis"'
            f' text-anchor="middle">{price // 100}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" \
width="{width}" height="{height}" role="img" aria-labelledby="t d">
<title id="t">Kâr uçurumu</title>
<desc id="d">Satış fiyatına göre net kâr; 300 ve 600 TL kargo eşiklerinde kâr düşer. \
Değerler engine/profit.py çıktısıdır.</desc>
<style>
.bg{{fill:#0d1b24}}.grid{{stroke:#1f3442;stroke-width:1}}
.axis{{fill:#7f97a6;font:12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.title{{fill:#e8f1f5;font:700 20px system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif}}
.sub{{fill:#8fb3c4;font:13px system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif}}
.lbl{{fill:#e8f1f5;font:600 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.drop{{fill:#ff8c9b;font:700 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.line{{fill:none;stroke:url(#g);stroke-width:3;stroke-linejoin:round;stroke-dasharray:3000;\
stroke-dashoffset:3000;animation:draw 2.4s ease-out forwards}}
.mark{{opacity:0;animation:show .5s ease-out forwards}}
.pulse{{fill:none;stroke:#ff5d73;stroke-width:2;transform-box:fill-box;transform-origin:center;\
animation:pulse 1.6s ease-out infinite}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}@keyframes show{{to{{opacity:1}}}}
@keyframes pulse{{0%{{transform:scale(1);opacity:1}}100%{{transform:scale(3.2);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.line{{animation:none;stroke-dashoffset:0}}\
.mark{{animation:none;opacity:1}}.pulse{{animation:none}}}}
</style>
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#2dd4bf"/>\
<stop offset="1" stop-color="#60a5fa"/></linearGradient></defs>
<rect class="bg" width="{width}" height="{height}" rx="18"/>
<text x="{left}" y="34" class="title">Kâr uçurumu: fiyatı artır, kârın düşsün</text>
<text x="{left}" y="54" class="sub">Net kâr (₺) · satış fiyatı 100–800 ₺ · %20 komisyon · \
120 ₺ maliyet · sentetik barem · kaynak: engine/profit.py</text>
<rect x="{left}" y="{y(0):.1f}" width="{width - left - right}" \
height="{height - bottom - y(0):.1f}" fill="#ff5d73" opacity=".07"/>
<text x="{width - right - 8}" y="{height - bottom - 10}" class="axis" text-anchor="end" \
fill="#ff8c9b">zarar bölgesi</text>
{"".join(grid)}
<polyline class="line" points="{points}"/>
{"".join(marks)}
</svg>
"""


def write(data_path=DATA_PATH, svg_path=SVG_PATH):
    data = build_data()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    svg_path.write_text(build_svg(data), encoding="utf-8")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    write()
