import pytest

from scripts.check_golden import calculate

pytestmark = pytest.mark.unit


def test_reconciliation_runner_uses_user_supplied_600_tl_anchor():
    # Expected figures come from the user's original plan, not the motor output.
    scenario = {
        "id": "PLAN-600",
        "marketplace": "demo_tr",
        "input": {
            "line_number": 1,
            "quantity": 1,
            "unit_price_gross": "600",
            "unit_cost_net": "250",
            "vat_percent": "20",
            "commission_percent": "20",
        },
    }
    actual = calculate(scenario)
    assert {
        key: actual[key]
        for key in (
            "net_sales",
            "commission",
            "shipping",
            "service",
            "withholding",
            "profit",
            "payout",
        )
    } == {
        "net_sales": 50000,
        "commission": 12000,
        "shipping": 6000,
        "service": 1000,
        "withholding": 500,
        "profit": 6000,
        "payout": 36700,
    }
