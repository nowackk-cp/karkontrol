"""Yalnız sentetik girdiler ve BOŞ insan inceleme şablonu; sonuç hesaplamaz."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    scenarios = []
    variants = [
        {},
        {"unit_price_gross": "0"},
        {"vat_percent": "0"},
        {"vat_percent": "1"},
        {"vat_percent": "10"},
        {"quantity": 2},
        {"quantity": 3},
        {"commission_percent": "0"},
        {"unit_price_gross": "299.99"},
        {"unit_price_gross": "300"},
        {"unit_price_gross": "300.01"},
        {"unit_price_gross": "600.01"},
        {"desi": "3.01"},
        {"desi": "3"},
        {"weight_kg": "4.01"},
        {"seller_discount": "100"},
        {"platform_coupon": "100"},
        {"seller_discount": "50", "platform_coupon": "50"},
        {"returned_quantity": 1},
        {"quantity": 3, "returned_quantity": 1},
        {"quantity": 3, "returned_quantity": 2},
        {"quantity": 3, "returned_quantity": 3},
        {"unit_price_gross": "0.01"},
        {"unit_price_gross": "0.05"},
        {"unit_cost_net": "0"},
        {"unit_cost_net": "1000"},
        {"unit_price_gross": "9999999.99"},
        {"commission_percent": "100"},
        {"cost_vat_percent": "0"},
        {"unit_price_gross": "1.01", "quantity": 7},
    ]
    for index in range(40):
        data = {
            "line_number": 1,
            "quantity": 1,
            "unit_price_gross": "600",
            "unit_cost_net": "250",
            "vat_percent": "20",
            "commission_percent": "20",
            "desi": "1",
            "weight_kg": "0",
            "seller_discount": "0",
            "platform_coupon": "0",
            "cost_vat_percent": "20",
            "returned_quantity": 0,
            "currency": "TRY",
            "exchange_rate": "1",
        }
        if index < 30:
            data.update(variants[index])
        else:
            data.update(
                {
                    "currency": "USD" if index % 2 else "EUR",
                    "exchange_rate": "40.123456",
                    "quantity": index - 29,
                    "returned_quantity": (index - 30) % 3,
                }
            )
        scenarios.append(
            {
                "id": f"SIP-{index + 1:02d}",
                "marketplace": "demo_tr" if index < 30 else "amazon_demo",
                "input": data,
            }
        )
    target = ROOT / "data" / "draft"
    target.mkdir(parents=True, exist_ok=True)
    (target / "inputs.json").write_text(
        json.dumps(
            {
                "status": "AI-authored synthetic inputs; no human-reviewed expected results",
                "scenarios": scenarios,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with (target / "manual_review.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(
            [
                "id",
                "net_sales",
                "commission",
                "shipping",
                "service",
                "withholding",
                "profit",
                "payout",
                "reviewer",
                "reviewed_at",
                "source",
            ]
        )
        writer.writerows([[case["id"], *([""] * 10)] for case in scenarios])
    print(f"{len(scenarios)} girdi; beklenen sonuç hücreleri boş.")


if __name__ == "__main__":
    main()
