from dataclasses import replace
from decimal import Decimal
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.profit import LineInput, allocate, calculate_order, money, shipping_fee

pytestmark = pytest.mark.unit
D = Decimal


def line(**changes):
    return replace(LineInput(1, 1, D("600"), D("250"), D("20"), D("20")), **changes)


def result(**changes):
    return calculate_order([line(**changes)])[0]


def test_user_supplied_600_tl_example():
    """Kaynak planın verdiği örnek; yeni AI altın beklentisi değildir."""
    r = result()
    assert (r.net_sales, r.commission, r.shipping, r.service, r.withholding) == (
        D("500"),
        D("120"),
        D("60"),
        D("10"),
        D("5"),
    )
    assert r.profit == D("60")
    assert r.payout == D("367")
    assert r.sales_vat == D("100")
    assert r.fee_vat == D("38")
    assert r.cost_vat == D("50")
    assert r.cash_profit == D("60.00")  # Kamu alanının verilen 600 TL örneğindeki değeri.
    assert_reference_accounting(r, 60000, 12000, 6000, 1000, 25000, 20)


@pytest.mark.parametrize(
    "gross,expected",
    [
        ("0", "30"),
        ("299.99", "30"),
        ("300", "30"),
        ("300.01", "60"),
        ("599.99", "60"),
        ("600", "60"),
        ("600.01", "80"),
        ("1000000", "80"),
    ],
)
def test_shipping_thresholds(gross, expected):
    assert shipping_fee(D(gross), D("0")) == D(expected)


@pytest.mark.parametrize(
    "desi,expected",
    [("0", "30"), ("2.99", "30"), ("3", "30"), ("3.01", "35"), ("4", "35"), ("4.01", "40")],
)
def test_desi_rounds_up(desi, expected):
    assert shipping_fee(D("100"), D(desi)) == D(expected)


@pytest.mark.parametrize(
    "value,expected", [("1.004", "1.00"), ("1.005", "1.01"), ("-1.005", "-1.01"), ("0.005", "0.01")]
)
def test_half_up(value, expected):
    assert money(D(value)) == D(expected)


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("quantity", 0, "quantity: pozitif tamsayı gerekli"),
        ("quantity", -1, "quantity: pozitif tamsayı gerekli"),
        ("quantity", True, "quantity: pozitif tamsayı gerekli"),
        ("quantity", 1.5, "quantity: pozitif tamsayı gerekli"),
        ("line_number", 0, "line_number: pozitif tamsayı gerekli"),
        ("line_number", True, "line_number: pozitif tamsayı gerekli"),
        ("returned_quantity", -1, "İade adedi geçersiz"),
        ("returned_quantity", 2, "İade adedi geçersiz"),
        ("returned_quantity", False, "İade adedi geçersiz"),
        ("unit_price_gross", D("NaN"), "unit_price_gross: sonlu, negatif olmayan Decimal gerekli"),
        (
            "unit_price_gross",
            D("Infinity"),
            "unit_price_gross: sonlu, negatif olmayan Decimal gerekli",
        ),
        (
            "unit_price_gross",
            D("-0.01"),
            "unit_price_gross: sonlu, negatif olmayan Decimal gerekli",
        ),
        ("unit_price_gross", 0.1, "unit_price_gross: sonlu, negatif olmayan Decimal gerekli"),
        ("unit_cost_net", D("-1"), "unit_cost_net: sonlu, negatif olmayan Decimal gerekli"),
        ("seller_discount", D("601"), "İndirim ve kupon brüt tutarı aşamaz"),
        ("platform_coupon", D("601"), "İndirim ve kupon brüt tutarı aşamaz"),
        ("vat_percent", D("101"), "vat_percent: üst sınır aşıldı"),
        (
            "commission_percent",
            D("-1"),
            "commission_percent: sonlu, negatif olmayan Decimal gerekli",
        ),
        ("cost_vat_percent", D("101"), "cost_vat_percent: üst sınır aşıldı"),
        ("desi", D("-1"), "desi: sonlu, negatif olmayan Decimal gerekli"),
        ("weight_kg", D("-1"), "weight_kg: sonlu, negatif olmayan Decimal gerekli"),
        ("currency", "GBP", "Para birimi veya kur geçersiz"),
        ("exchange_rate", D("0"), "Para birimi veya kur geçersiz"),
        ("exchange_rate", D("2"), "TRY kuru 1 olmalı"),
        ("unit_price_gross", D("10000000000"), "unit_price_gross: üst sınır aşıldı"),
    ],
)
def test_invalid_input_rejected(field, value, message):
    with pytest.raises(ValueError, match=message):
        result(**{field: value})


def test_discount_and_platform_funding_are_distinct():
    assert result(platform_coupon=D("100")) == result()
    assert result(seller_discount=D("100")).gross_sales == D("500")


def test_partial_and_full_return():
    partial = result(quantity=2, returned_quantity=1)
    assert partial.gross_sales == D("600")
    assert partial.cost == D("250")
    assert partial.shipping == D("160")  # 1,200 TL first shipment and a return shipment
    assert partial.service == D("5")
    full = result(returned_quantity=1)
    assert full.net_sales == full.commission == full.cost == full.withholding == D("0")
    assert full.profit == D("-120")
    assert_reference_accounting(full, 0, 0, 12000, 0, 0, 20)


def test_zero_value_returns_allocate_to_returned_lines_only():
    a = line(unit_price_gross=D("0"), line_number=1, returned_quantity=0)
    b = replace(a, line_number=2, returned_quantity=1)
    results = calculate_order([b, a])
    assert [r.shipping for r in results] == [D("15"), D("45")]


def test_order_shipping_once_and_cent_tie_is_stable():
    lines = [line(line_number=i, unit_price_gross=D("0.01"), desi=D("0")) for i in (3, 2, 1)]
    results = calculate_order(lines)
    assert sum(r.shipping for r in results) == D("30")
    assert [r.service for r in results] == [D("3.34"), D("3.33"), D("3.33")]
    for row, service in zip(results, (334, 333, 333), strict=True):
        assert_reference_accounting(row, 1, 0, 1000, service, 25000, 20)


def test_weight_takes_precedence_over_desi():
    assert result(desi=D("2"), weight_kg=D("4.01")).shipping == D("70")


@pytest.mark.parametrize("vat", ["0", "1", "10", "20", "100"])
def test_vat_split_is_exact(vat):
    r = result(vat_percent=D(vat))
    assert r.net_sales + r.sales_vat == r.gross_sales
    assert_reference_accounting(r, 60000, 12000, 6000, 1000, 25000, int(vat))


def test_empty_duplicate_mixed_currency_and_unknown_marketplace():
    for lines, message in (
        ([], "Sipariş boş veya satır numaraları tekrarlı"),
        ([line(), line()], "Sipariş boş veya satır numaraları tekrarlı"),
        (
            [line(), line(line_number=2, currency="USD", exchange_rate=D("40"))],
            "Bir siparişin para birimi ve kuru aynı olmalı",
        ),
    ):
        with pytest.raises(ValueError, match=message):
            calculate_order(lines)
    with pytest.raises(ValueError, match="Pazaryeri desteklenmiyor"):
        calculate_order([line()], marketplace="unknown")
    with pytest.raises(ValueError, match="Demo TRY mağazasında yabancı para kullanılamaz"):
        calculate_order([line(currency="USD", exchange_rate=D("40"))])


@pytest.mark.parametrize("currency,rate", [("TRY", "1"), ("USD", "40"), ("EUR", "45.123456")])
def test_amazon_fixed_rate_and_fee(currency, rate):
    r = calculate_order(
        [line(currency=currency, exchange_rate=D(rate))], marketplace="amazon_demo"
    )[0]
    gross_cents = integer_round(Fraction(60000) * Fraction(rate))
    cost_cents = integer_round(Fraction(25000) * Fraction(rate))
    commission_cents = integer_round(Fraction(gross_cents, 5))
    assert r.gross_sales == D(gross_cents) / 100
    assert r.shipping == D("80")
    assert r.service == D("0")
    assert_reference_accounting(r, gross_cents, commission_cents, 8000, 0, cost_cents, 20)


@pytest.mark.parametrize(
    "total,weights,message",
    [
        (D("-1"), [D("1")], "total: sonlu, negatif olmayan Decimal gerekli"),
        (D("1"), [], "Dağıtım ağırlıkları geçersiz"),
        (D("1"), [D("-1")], "weight: sonlu, negatif olmayan Decimal gerekli"),
    ],
)
def test_bad_allocation(total, weights, message):
    with pytest.raises(ValueError, match=message):
        allocate(total, weights)


def test_largest_remainder_follows_weight_not_input_position():
    assert allocate(D("0.01"), [D("1"), D("3")]) == [D("0"), D("0.01")]
    assert allocate(D("0.01"), [D("3"), D("1")]) == [D("0.01"), D("0")]
    assert allocate(D("1.01"), [D("0"), D("0")]) == [D("0.51"), D("0.50")]
    with pytest.raises(ValueError, match="weight: sonlu, negatif olmayan Decimal gerekli"):
        allocate(D("1"), [1.5])


def test_maximum_quantity_boundary_and_nondefault_cost_vat():
    zero = line(
        quantity=2_147_483_647,
        line_number=2_147_483_647,
        unit_price_gross=D("0"),
        unit_cost_net=D("0"),
        desi=D("0"),
    )
    assert calculate_order([zero])[0].gross_sales == D("0")
    for name in ("quantity", "line_number"):
        with pytest.raises(ValueError, match=f"{name}: pozitif tamsayı gerekli"):
            calculate_order([replace(zero, **{name: 2_147_483_648})])
    assert result(cost_vat_percent=D("10")).cost_vat == D("25")
    assert result(cost_vat_percent=D("0")).cost_vat == D("0")
    assert result(quantity=2, returned_quantity=1, cost_vat_percent=D("10")).cost_vat == D("25")


def integer_round(value: Fraction) -> int:
    """Bağımsız aritmetik yolu: Fraction -> tamsayı kuruş, Decimal motorunu çağırmaz."""
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def assert_reference_accounting(r, gross, commission, shipping, service, cost, vat, cost_vat=20):
    """Kural girdilerinden bağımsız tamsayı/Fraction KDV ve hakediş oracle'ı."""
    net = integer_round(Fraction(gross * 100, 100 + vat))
    fee_vat = sum(integer_round(Fraction(item, 5)) for item in (commission, shipping, service))
    withholding = integer_round(Fraction(net, 100))
    expected = {
        "gross_sales": gross,
        "net_sales": net,
        "sales_vat": gross - net,
        "commission": commission,
        "shipping": shipping,
        "service": service,
        "cost": cost,
        "cost_vat": integer_round(Fraction(cost * cost_vat, 100)),
        "fee_vat": fee_vat,
        "withholding": withholding,
        "payout": gross - commission - shipping - service - fee_vat - withholding,
        "profit": net - commission - shipping - service - cost,
    }
    for name, cents in expected.items():
        assert getattr(r, name) * 100 == cents, name


@pytest.mark.property
@given(
    price=st.integers(0, 100_000_000),
    cost=st.integers(0, 100_000_000),
    quantity=st.integers(1, 100),
    returned=st.integers(0, 100),
    vat=st.sampled_from([0, 1, 10, 20]),
    commission=st.integers(0, 100),
)
@settings(max_examples=300, deadline=None)
def test_fraction_reference_for_profit_payout_and_vat(
    price, cost, quantity, returned, vat, commission
):
    returned = min(returned, quantity)
    remaining = quantity - returned
    gross = price * remaining
    net = integer_round(Fraction(gross * 100, 100 + vat))
    fees = integer_round(Fraction(gross * commission, 100))
    original = price * quantity
    shipping = 3000 if original <= 30000 else (6000 if original <= 60000 else 8000)
    shipping += max(0, quantity - 3) * 500
    if returned:
        shipping *= 2
    service = integer_round(Fraction(1000 * remaining, quantity))
    withholding = integer_round(Fraction(net, 100))
    fee_vat = sum(integer_round(Fraction(value, 5)) for value in (fees, shipping, service))
    r = result(
        unit_price_gross=D(price) / 100,
        unit_cost_net=D(cost) / 100,
        quantity=quantity,
        returned_quantity=returned,
        vat_percent=D(vat),
        commission_percent=D(commission),
    )
    assert int(r.profit * 100) == net - fees - shipping - service - cost * remaining
    assert int(r.payout * 100) == gross - fees - shipping - service - fee_vat - withholding
    assert_reference_accounting(r, gross, fees, shipping, service, cost * remaining, vat)


@pytest.mark.property
@given(
    cents=st.integers(0, 100_000_000),
    weights=st.lists(st.integers(0, 10000), min_size=1, max_size=50),
)
def test_allocation_conserves_every_cent(cents, weights):
    result = allocate(D(cents) / 100, list(map(D, weights)))
    assert sum(result) == D(cents) / 100
    assert all(value >= 0 and value == money(value) for value in result)
