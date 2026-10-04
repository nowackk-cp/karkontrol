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
def test_draft_input_cash_identity(case):
    raw = case["input"]
    converted = {
        name: Decimal(value) if isinstance(value, str) and name != "currency" else value
        for name, value in raw.items()
    }
    result = calculate_order([LineInput(**converted)], marketplace=case["marketplace"])[0]
    assert result.cash_profit == result.profit
    assert result.shipping >= 0
    assert result.gross_sales == result.net_sales + result.sales_vat
