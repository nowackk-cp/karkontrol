"""Sentetik uygulama sözleşmesi regresyonları; insan altın verisi değildir."""

import re
from dataclasses import fields, replace
from decimal import Decimal, Inexact, InvalidOperation, Rounded, localcontext
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.profit import LineInput, allocate, calculate_order, money, shipping_fee

pytestmark = pytest.mark.unit
D = Decimal


def line(**changes):
    return replace(LineInput(1, 1, D("600.00"), D("250.00"), D("20"), D("20")), **changes)


def test_allocate_equal_remainders_prefer_lower_line():
    """KURALLAR_v1 §6: üç kalan da tam 1/3; düşük satır önce gelir."""
    assert allocate(D("10.00"), [D("100"), D("10"), D("10")]) == [
        D("8.34"),
        D("0.83"),
        D("0.83"),
    ]


def test_return_allocation_preserves_equal_rational_remainders():
    inputs = [
        line(
            line_number=index,
            quantity=3,
            unit_price_gross=D(price),
            seller_discount=D(discount),
            returned_quantity=1,
            desi=D("0"),
        )
        for index, price, discount in ((1, "7", "14"), (2, "1", "2"), (3, "1", "2"))
    ]
    rows = assert_order_matches_reference(inputs)
    # 30 TL gidiş/dönüş başına 7:1:1; her kalan tam 1/3.
    assert [row.shipping for row in rows] == [D("46.68"), D("6.66"), D("6.66")]


@pytest.mark.parametrize("precision", [6, 28, 50])
def test_allocation_tie_does_not_depend_on_decimal_precision(precision):
    with localcontext() as context:
        context.prec = precision
        assert allocate(D("10.00"), [D("100"), D("10"), D("10")]) == [
            D("8.34"),
            D("0.83"),
            D("0.83"),
        ]


@pytest.mark.parametrize(
    "field", ["unit_price_gross", "unit_cost_net", "seller_discount", "platform_coupon"]
)
def test_subcent_money_input_is_rejected(field):
    with pytest.raises(ValueError, match=rf"{field}: kuruş altı para kabul edilmez"):
        calculate_order([line(**{field: D("300.004")})])


@pytest.mark.parametrize("value", ["-0.00", "-0.004", "0"])
def test_money_normalizes_zero(value):
    rounded = money(D(value))
    assert rounded == D("0.00")
    assert not rounded.is_signed()
    assert rounded.as_tuple().exponent == -2


def test_every_output_money_has_cent_scale_and_normalized_zero():
    rows = calculate_order(
        [line(unit_price_gross=D("-0.00"), unit_cost_net=D("-0.00"), desi=D("0"))]
    )
    for row in rows:
        for field in fields(row):
            if field.name == "line_number":
                continue
            value = getattr(row, field.name)
            assert isinstance(value, Decimal), field.name
            assert value.as_tuple().exponent == -2, field.name
            if value == 0:
                assert not value.is_signed(), field.name


def round_cents(value):
    """Pozitif rasyonel tutarı HALF_UP ile tamsayı kuruşa çevir."""
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def reference_allocation(cents, weights):
    """Decimal motorundan bağımsız, sırayla en büyük kalanı seçen oracle."""
    weights = list(map(Fraction, weights))
    if not sum(weights):
        weights = [Fraction(1)] * len(weights)
    exact = [cents * weight / sum(weights) for weight in weights]
    allocated = [value.numerator // value.denominator for value in exact]
    remainders = [value - whole for value, whole in zip(exact, allocated, strict=True)]
    for _ in range(cents - sum(allocated)):
        index = max(range(len(weights)), key=remainders.__getitem__)
        allocated[index] += 1
        remainders[index] = Fraction(-1)
    return allocated


def reference_order(inputs, marketplace="demo_tr"):
    """KURALLAR_v1 §§2–8/v2 aritmetiği; yalnız Fraction ve tamsayı kuruş."""
    inputs = sorted(inputs, key=lambda item: item.line_number)
    originals = [
        round_cents(
            (Fraction(item.unit_price_gross) * item.quantity - Fraction(item.seller_discount))
            * Fraction(item.exchange_rate)
            * 100
        )
        for item in inputs
    ]
    desi = sum(
        max(Fraction(item.desi), Fraction(item.weight_kg)) * item.quantity for item in inputs
    )
    units = (desi.numerator + desi.denominator - 1) // desi.denominator
    freight = 8000
    if marketplace == "demo_tr":
        freight = 3000 if sum(originals) <= 30000 else (6000 if sum(originals) <= 60000 else 8000)
        freight += max(0, units - 3) * 500
    weights = originals if sum(originals) else [item.quantity for item in inputs]
    outbound = reference_allocation(freight, weights)
    service = reference_allocation(0 if marketplace == "amazon_demo" else 1000, weights)
    returned_weights = [
        Fraction(gross * item.returned_quantity, item.quantity)
        for gross, item in zip(originals, inputs, strict=True)
    ]
    if not sum(returned_weights):
        returned_weights = [Fraction(item.returned_quantity) for item in inputs]
    inbound = (
        reference_allocation(freight, returned_weights)
        if sum(returned_weights)
        else [0] * len(inputs)
    )
    expected = []
    for index, item in enumerate(inputs):
        remaining = item.quantity - item.returned_quantity
        gross = round_cents(Fraction(originals[index] * remaining, item.quantity))
        net = round_cents(Fraction(gross) * 100 / (100 + Fraction(item.vat_percent)))
        commission = round_cents(Fraction(gross) * Fraction(item.commission_percent) / 100)
        shipping = outbound[index] + inbound[index]
        fee = round_cents(Fraction(service[index] * remaining, item.quantity))
        cost = round_cents(
            Fraction(item.unit_cost_net) * remaining * Fraction(item.exchange_rate) * 100
        )
        fee_vat = sum(round_cents(Fraction(amount, 5)) for amount in (commission, shipping, fee))
        withholding = round_cents(Fraction(net, 100))
        expected.append(
            {
                "gross_sales": gross,
                "net_sales": net,
                "sales_vat": gross - net,
                "commission": commission,
                "shipping": shipping,
                "service": fee,
                "cost": cost,
                "cost_vat": round_cents(Fraction(cost) * Fraction(item.cost_vat_percent) / 100),
                "fee_vat": fee_vat,
                "withholding": withholding,
                "profit": net - commission - shipping - fee - cost,
                "payout": gross - commission - shipping - fee - fee_vat - withholding,
            }
        )
    return expected


def assert_order_matches_reference(inputs, marketplace="demo_tr"):
    rows = calculate_order(inputs, marketplace=marketplace)
    assert [row.line_number for row in rows] == sorted(item.line_number for item in inputs)
    for row, expected in zip(rows, reference_order(inputs, marketplace), strict=True):
        for name, cents in expected.items():
            value = getattr(row, name)
            assert Fraction(value) * 100 == cents, (row.line_number, name)
            assert isinstance(value, Decimal), name
            assert value.as_tuple().exponent == -2, name
    return rows


@pytest.mark.parametrize("currency,rate", [("USD", "40"), ("EUR", "45.123456")])
def test_fx_cost_discount_profit_and_payout(currency, rate):
    inputs = [
        line(
            quantity=2,
            returned_quantity=1,
            unit_price_gross=D("600.00"),
            unit_cost_net=D("250.00"),
            seller_discount=D("25.00"),
            platform_coupon=D("10.00"),
            currency=currency,
            exchange_rate=D(rate),
        )
    ]
    row = assert_order_matches_reference(inputs, "amazon_demo")[0]
    if currency == "USD":
        # Talepteki örnek: 250 USD × 40 = 10.000,00 TRY kalan maliyet.
        assert row.cost == D("10000.00")
    funded = replace(inputs[0], platform_coupon=D("0.00"))
    assert calculate_order([funded], marketplace="amazon_demo")[0] == row


@pytest.mark.parametrize(
    "inputs",
    [
        [
            line(line_number=1, unit_price_gross=D("100.00"), desi=D("1.5")),
            line(line_number=2, unit_price_gross=D("200.00"), desi=D("1.5")),
        ],
        [
            line(line_number=1, unit_price_gross=D("400.00"), seller_discount=D("100.00")),
            line(line_number=2, unit_price_gross=D("250.00"), platform_coupon=D("50.00")),
        ],
        [
            line(line_number=index, unit_price_gross=price, vat_percent=vat)
            for index, price, vat in (
                (1, D("100.00"), D("20")),
                (2, D("10.00"), D("10")),
                (3, D("10.00"), D("1")),
            )
        ],
        [
            line(line_number=1, quantity=3, returned_quantity=1, seller_discount=D("10.01")),
            line(line_number=2, unit_price_gross=D("99.99"), returned_quantity=1, desi=D("0.1")),
        ],
        [
            line(line_number=1, unit_price_gross=D("0.00"), quantity=2, returned_quantity=1),
            line(line_number=2, unit_price_gross=D("0.00"), returned_quantity=1),
        ],
    ],
    ids=["total-desi", "discount-barem", "mixed-vat-tie", "partial-returns", "zero-returns"],
)
def test_multiline_rule_examples(inputs):
    assert_order_matches_reference(inputs)


def test_supplied_multiline_rounding_examples():
    assert allocate(D("0.11"), [D("1"), D("3")]) == [D("0.03"), D("0.08")]
    desi_rows = calculate_order(
        [line(line_number=index, unit_price_gross=D("100.00"), desi=D("1.5")) for index in (1, 2)]
    )
    assert sum(row.shipping for row in desi_rows) == D("30.00")
    discounted = calculate_order([line(unit_price_gross=D("650.00"), seller_discount=D("100.00"))])
    assert discounted[0].shipping == D("60.00")


def test_price_increase_can_lower_profit_at_shipping_threshold():
    lower = calculate_order([line(unit_price_gross=D("300.00"))])[0]
    higher = calculate_order([line(unit_price_gross=D("300.01"))])[0]
    assert lower.shipping == D("30.00")
    assert higher.shipping == D("60.00")
    assert higher.profit < lower.profit
    assert lower.profit - higher.profit == D("29.99")


@pytest.mark.parametrize("bad_weight", [D("NaN"), D("Infinity"), "1", 1.5])
def test_invalid_allocation_weight_has_clear_error(bad_weight):
    with pytest.raises(ValueError, match="weight: sonlu, negatif olmayan Decimal gerekli"):
        allocate(D("1.00"), [bad_weight])


@pytest.mark.parametrize("field", ["gross", "desi"])
@pytest.mark.parametrize("invalid", [D("-0.01"), D("NaN"), D("Infinity"), "1", 1.5])
def test_shipping_input_errors_name_the_invalid_field(field, invalid):
    arguments = {"gross": D("100.00"), "desi": D("1")}
    arguments[field] = invalid
    with pytest.raises(ValueError, match=f"{field}: sonlu, negatif olmayan Decimal gerekli"):
        shipping_fee(**arguments)


def test_allocation_largest_fraction_can_belong_to_smaller_weight():
    assert allocate(D("0.02"), [D("1"), D("2")]) == [D("0.01"), D("0.01")]


@pytest.mark.parametrize("value", ["300.000", "-0.000"])
def test_trailing_zeros_do_not_change_money_precision(value):
    assert_order_matches_reference([line(unit_price_gross=D(value))])


@pytest.mark.parametrize("digits", [51, 101])
@pytest.mark.parametrize("quantity,returned", [(1, 0), (2, 1), (3, 2), (3, 1)])
def test_fx_half_cent_boundary_uses_exact_rate(digits, quantity, returned):
    """ENG-002: kabul edilen uzun kurda erken yuvarlama yapılmamalı."""
    rate = D("1.004" + "9" * (digits - 4))
    assert_order_matches_reference(
        [
            line(
                quantity=quantity,
                returned_quantity=returned,
                unit_price_gross=D("1.00"),
                unit_cost_net=D("1.00"),
                vat_percent=D("0"),
                commission_percent=D("0"),
                currency="USD",
                exchange_rate=rate,
            )
        ],
        "amazon_demo",
    )


def decimal_above_fraction(value, decimal_places):
    """Eşik üstündeki sonlu Decimal girdisini context kullanmadan oluştur."""
    numerator = value.numerator * 10**decimal_places
    coefficient = (numerator + value.denominator - 1) // value.denominator
    return D((0, tuple(map(int, str(coefficient))), -decimal_places))


@pytest.mark.parametrize("digits", [51, 101])
def test_vat_near_half_cent_uses_exact_divisor(digits):
    # 3 / (1 + (19900/401)/100) = 2.005; az yüksek KDV neti eşik altına indirir.
    vat = decimal_above_fraction(Fraction(19900, 401), digits)
    assert Fraction(vat) > Fraction(19900, 401)
    assert_order_matches_reference(
        [line(unit_price_gross=D("3.00"), unit_cost_net=D("0.00"), vat_percent=vat)]
    )


@pytest.mark.parametrize("digits", [51, 101])
@pytest.mark.parametrize("field", ["commission_percent", "cost_vat_percent"])
def test_percentage_near_half_cent_uses_exact_rate(digits, field):
    percentage = D("0.4" + "9" * (digits - 1))
    assert Fraction(percentage) < Fraction(1, 2)
    assert_order_matches_reference(
        [line(unit_price_gross=D("1.00"), unit_cost_net=D("1.00"), **{field: percentage})]
    )


@pytest.mark.parametrize("digits", [51, 101])
@pytest.mark.parametrize("field", ["desi", "weight_kg"])
@pytest.mark.parametrize("quantity,whole,fractional", [(1, "1", "5"), (2, "0", "75")])
def test_total_desi_ceiling_preserves_small_positive_remainder(
    digits, field, quantity, whole, fractional
):
    lower = D(f"{whole}.{fractional}")
    upper = D(f"{whole}.{fractional}" + "0" * digits + "1")
    inputs = (
        [
            line(line_number=1, quantity=quantity, desi=D("0"), **{field: lower}),
            line(line_number=2, quantity=quantity, desi=D("0"), **{field: upper}),
        ]
        if field == "weight_kg"
        else [
            line(line_number=1, quantity=quantity, desi=lower),
            line(line_number=2, quantity=quantity, desi=upper),
        ]
    )
    assert_order_matches_reference(inputs)


@pytest.mark.parametrize("precision", [1, 6, 28])
def test_public_money_allocation_and_shipping_are_context_independent(precision):
    value = D("9999999999.995")
    total = D("9999999999.99")
    with localcontext() as context:
        context.prec = precision
        assert money(value) == D("10000000000.00")
        shares = allocate(total, [D("1"), D("1"), D("1")])
        assert sum(map(Fraction, shares)) == Fraction(total)
        assert [Fraction(item) * 100 for item in shares] == reference_allocation(
            999999999999, [1, 1, 1]
        )
        assert shipping_fee(D("100.00"), D("9999999999.99")) == D("50000000015.00")


def test_money_keeps_nonfinite_decimal_compatibility():
    assert money(D("NaN")).is_qnan()
    for value in (D("sNaN"), D("Infinity")):
        with pytest.raises(InvalidOperation):
            money(value)


def test_financial_rounding_does_not_trigger_ambient_decimal_traps():
    inputs = [
        line(
            quantity=3,
            returned_quantity=1,
            currency="EUR",
            exchange_rate=D("1.004" + "9" * 97),
            commission_percent=D("0.4" + "9" * 100),
            cost_vat_percent=D("0.4" + "9" * 100),
        )
    ]
    with localcontext() as context:
        context.prec = 1
        context.traps[Inexact] = True
        context.traps[Rounded] = True
        assert_order_matches_reference(inputs, "amazon_demo")


@pytest.mark.parametrize("precision", [1, 6, 28])
def test_large_order_and_cash_identity_preserve_exact_cents(precision):
    inputs = [
        line(
            quantity=2_147_483_647,
            returned_quantity=1,
            unit_price_gross=D("9999999999.99"),
            unit_cost_net=D("9999999999.98"),
            currency="USD",
            exchange_rate=D("9999999999.99"),
        )
    ]
    with localcontext() as context:
        context.prec = precision
        row = assert_order_matches_reference(inputs, "amazon_demo")[0]
        expected = reference_order(inputs, "amazon_demo")[0]
        assert Fraction(row.cash_profit) * 100 == expected["profit"]


@pytest.mark.parametrize(
    "operation,message",
    [
        (lambda: line(returned_quantity=2).validate(), "İade adedi geçersiz"),
        (lambda: line(currency="GBP").validate(), "Para birimi veya kur geçersiz"),
        (lambda: line(exchange_rate=D("2")).validate(), "TRY kuru 1 olmalı"),
        (
            lambda: line(seller_discount=D("601.00")).validate(),
            "İndirim ve kupon brüt tutarı aşamaz",
        ),
        (lambda: allocate(D("1.00"), []), "Dağıtım ağırlıkları geçersiz"),
        (
            lambda: shipping_fee(D("600.00"), D("1"), marketplace="unknown"),
            "Pazaryeri desteklenmiyor",
        ),
        (lambda: calculate_order([]), "Sipariş boş veya satır numaraları tekrarlı"),
        (
            lambda: calculate_order(
                [line(), line(line_number=2, currency="USD", exchange_rate=D("40"))]
            ),
            "Bir siparişin para birimi ve kuru aynı olmalı",
        ),
        (
            lambda: calculate_order([line(currency="USD", exchange_rate=D("40"))]),
            "Demo TRY mağazasında yabancı para kullanılamaz",
        ),
    ],
)
def test_error_message_contract_has_exact_anchors(operation, message):
    with pytest.raises(ValueError, match=rf"\A{re.escape(message)}\Z"):
        operation()


input_rows = st.lists(
    st.tuples(
        st.integers(0, 100000),
        st.integers(0, 100000),
        st.integers(1, 8),
        st.integers(0, 8),
        st.sampled_from([0, 1, 10, 20]),
        st.integers(0, 100),
        st.integers(0, 50),
    ),
    min_size=2,
    max_size=5,
)


def property_inputs(data):
    return [
        line(
            line_number=index,
            unit_price_gross=D(price) / 100,
            unit_cost_net=D(cost) / 100,
            quantity=quantity,
            returned_quantity=min(returned, quantity),
            vat_percent=D(vat),
            commission_percent=D(commission),
            desi=D(desi) / 10,
        )
        for index, (price, cost, quantity, returned, vat, commission, desi) in enumerate(data, 1)
    ]


@pytest.mark.property
@given(data=input_rows, permutation_data=st.data())
@settings(max_examples=150, deadline=None)
def test_multiline_reference_and_input_order_invariance(data, permutation_data):
    inputs = property_inputs(data)
    rows = assert_order_matches_reference(inputs)
    permuted = permutation_data.draw(st.permutations(inputs))
    assert calculate_order(permuted) == rows
    for row in rows:
        assert all(
            getattr(row, name) >= 0
            for name in ("commission", "shipping", "service", "cost", "fee_vat", "withholding")
        )


@pytest.mark.property
@given(data=input_rows, extra_cost_cents=st.integers(1, 100000))
@settings(max_examples=100, deadline=None)
def test_cost_increase_reduces_profit_by_remaining_cost(data, extra_cost_cents):
    inputs = property_inputs(data)
    before = calculate_order(inputs)
    after = calculate_order(
        [
            replace(item, unit_cost_net=item.unit_cost_net + D(extra_cost_cents) / 100)
            for item in inputs
        ]
    )
    for original, changed, item in zip(before, after, inputs, strict=True):
        expected_drop = D(extra_cost_cents * (item.quantity - item.returned_quantity)) / 100
        assert original.profit - changed.profit == expected_drop
        assert original.payout == changed.payout


@pytest.mark.property
@given(data=input_rows)
@settings(max_examples=100, deadline=None)
def test_full_return_cancels_revenue_commission_and_withholding(data):
    inputs = [replace(item, returned_quantity=item.quantity) for item in property_inputs(data)]
    rows = assert_order_matches_reference(inputs)
    for row in rows:
        assert row.gross_sales == row.net_sales == row.commission == row.withholding == D("0.00")
        assert row.service == row.cost == row.cost_vat == row.sales_vat == D("0.00")


@pytest.mark.property
@given(first=input_rows, second=input_rows)
@settings(max_examples=100, deadline=None)
def test_two_order_totals_equal_independent_rounded_rows(first, second):
    inputs = [property_inputs(first), property_inputs(second)]
    results = [calculate_order(order) for order in inputs]
    oracle_rows = [row for order in inputs for row in reference_order(order)]
    for name in ("gross_sales", "net_sales", "profit", "payout", "sales_vat", "fee_vat"):
        assert sum(getattr(row, name) * 100 for order in results for row in order) == sum(
            row[name] for row in oracle_rows
        )
