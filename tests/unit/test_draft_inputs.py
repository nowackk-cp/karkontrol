import json
from decimal import Decimal
from pathlib import Path

import pytest

from engine.profit import LineInput, calculate_order

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "data/draft/inputs.json").read_text(encoding="utf-8")
)["scenarios"]


@pytest.mark.unit
@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_draft_input_structure_and_supported_money(case):
    raw = case["input"]
    converted = {
        name: Decimal(value) if isinstance(value, str) and name != "currency" else value
        for name, value in raw.items()
    }
    result = calculate_order([LineInput(**converted)], marketplace=case["marketplace"])[0]
    # This input inventory checks types/invariants, not an independent financial oracle.
    assert all(
        isinstance(getattr(result, field), Decimal)
        and getattr(result, field).as_tuple().exponent == -2
        for field in ("profit", "payout", "net_sales", "shipping")
    )
    assert result.shipping >= 0
    assert result.gross_sales == result.net_sales + result.sales_vat
