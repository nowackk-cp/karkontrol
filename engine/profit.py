"""Kurallar: docs/KURALLAR.md."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

ZERO = Decimal("0.00")
CENT = Decimal("0.01")
HUNDRED = Decimal("100")
VERSION = "demo-v1"


def money(value: Decimal) -> Decimal:
    if not value.is_finite():
        return value.quantize(CENT, rounding=ROUND_HALF_UP)
    return _decimal_from_coefficient(_round_half_up(Fraction(value) * 100))


def _round_half_up(value: Fraction) -> int:
    """Tam rasyonelin en yakın tamsayısı; yarımda sıfırdan uzaklaşır."""
    quotient, remainder = divmod(abs(value.numerator), value.denominator)
    rounded = quotient + int(2 * remainder >= value.denominator)
    return -rounded if value < 0 else rounded


def _decimal_from_coefficient(value: int, exponent: int = -2) -> Decimal:
    """Decimal context'i kullanmadan tam katsayı ve ölçek oluştur."""
    digits = Decimal(value).as_tuple()
    return Decimal((digits.sign, digits.digits, exponent))


def validate_decimal(value, name, *, maximum=None):
    if not isinstance(value, Decimal) or not value.is_finite() or value < ZERO:
        raise ValueError(f"{name}: sonlu, negatif olmayan Decimal gerekli")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name}: üst sınır aşıldı")


@dataclass(frozen=True)
class LineInput:
    line_number: int
    quantity: int
    unit_price_gross: Decimal
    unit_cost_net: Decimal
    vat_percent: Decimal
    commission_percent: Decimal
    seller_discount: Decimal = ZERO
    platform_coupon: Decimal = ZERO
    returned_quantity: int = 0
    desi: Decimal = Decimal("1")
    weight_kg: Decimal = ZERO
    cost_vat_percent: Decimal = Decimal("20")
    currency: str = "TRY"
    exchange_rate: Decimal = Decimal("1")

    def validate(self):
        for name in ("line_number", "quantity"):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= 2_147_483_647:
                raise ValueError(f"{name}: pozitif tamsayı gerekli")
        if (
            type(self.returned_quantity) is not int
            or not 0 <= self.returned_quantity <= self.quantity
        ):
            raise ValueError("İade adedi geçersiz")
        for name in (
            "unit_price_gross",
            "unit_cost_net",
            "seller_discount",
            "platform_coupon",
            "desi",
            "weight_kg",
            "exchange_rate",
        ):
            validate_decimal(getattr(self, name), name, maximum=Decimal("9999999999.99"))
        for name in ("vat_percent", "commission_percent", "cost_vat_percent"):
            validate_decimal(getattr(self, name), name, maximum=HUNDRED)
        for name in ("unit_price_gross", "unit_cost_net", "seller_discount", "platform_coupon"):
            value = getattr(self, name)
            if value != money(value):
                raise ValueError(f"{name}: kuruş altı para kabul edilmez")
        if self.currency not in ("TRY", "USD", "EUR") or self.exchange_rate <= ZERO:
            raise ValueError("Para birimi veya kur geçersiz")
        if self.currency == "TRY" and self.exchange_rate != Decimal("1"):
            raise ValueError("TRY kuru 1 olmalı")
        if (
            Fraction(self.seller_discount) + Fraction(self.platform_coupon)
            > Fraction(self.unit_price_gross) * self.quantity
        ):
            raise ValueError("İndirim ve kupon brüt tutarı aşamaz")


@dataclass(frozen=True)
class LineResult:
    line_number: int
    gross_sales: Decimal
    net_sales: Decimal
    commission: Decimal
    shipping: Decimal
    service: Decimal
    cost: Decimal
    withholding: Decimal
    profit: Decimal
    payout: Decimal
    sales_vat: Decimal
    fee_vat: Decimal
    cost_vat: Decimal

    @property
    def cash_profit(self):
        """Uyumluluk için cebirsel kâr eşitliği; bağımsız hesap doğrulaması değildir."""
        exponent = min(
            value.as_tuple().exponent
            for value in (
                self.payout,
                self.cost,
                self.cost_vat,
                self.sales_vat,
                self.fee_vat,
                self.withholding,
            )
        )
        exact = (
            Fraction(self.payout)
            - Fraction(self.cost)
            - Fraction(self.cost_vat)
            - (Fraction(self.sales_vat) - Fraction(self.fee_vat) - Fraction(self.cost_vat))
            + Fraction(self.withholding)
        )
        coefficient = exact / Fraction(10) ** exponent
        return _decimal_from_coefficient(coefficient.numerator, exponent)


def allocate(total: Decimal, weights: list[Decimal]) -> list[Decimal]:
    """Kuruşların tamamını korur; eşit kalanlarda liste sırası belirleyicidir."""
    if not weights:
        raise ValueError("Dağıtım ağırlıkları geçersiz")
    for weight in weights:
        validate_decimal(weight, "weight")
    validate_decimal(total, "total")
    if not any(weights):
        weights = [Decimal("1")] * len(weights)
    cents = _round_half_up(Fraction(total) * 100)
    return _allocate_cents(cents, [Fraction(weight) for weight in weights])


def _allocate_cents(cents: int, exact_weights: list[Fraction]) -> list[Decimal]:
    return [
        _decimal_from_coefficient(value) for value in _allocate_integer_cents(cents, exact_weights)
    ]


def _allocate_integer_cents(cents: int, exact_weights: list[Fraction]) -> list[int]:
    # Decimal bölmesi aynı rasyonel kalana farklı son basamaklar verebilir.
    # Fraction ve divmod, eşit kalanları context precision'dan bağımsız tutar.
    weight_sum = sum(exact_weights)
    shares = [divmod(cents * weight, weight_sum) for weight in exact_weights]
    base = [quotient for quotient, _ in shares]
    ranked = sorted(range(len(base)), key=lambda i: (-shares[i][1], i))
    for index in ranked[: cents - sum(base)]:
        base[index] += 1
    return base


def shipping_fee(gross: Decimal, desi: Decimal, *, marketplace="demo_tr") -> Decimal:
    validate_decimal(gross, "gross")
    validate_decimal(desi, "desi")
    return _decimal_from_coefficient(_shipping_cents(Fraction(gross), Fraction(desi), marketplace))


def _shipping_cents(gross: Fraction, desi: Fraction, marketplace: str) -> int:
    if marketplace == "amazon_demo":
        return 8000
    if marketplace != "demo_tr":
        raise ValueError("Pazaryeri desteklenmiyor")
    base = 3000 if gross <= 300 else (6000 if gross <= 600 else 8000)
    units = -(-desi.numerator // desi.denominator)
    return base + max(0, units - 3) * 500


def calculate_order(lines: list[LineInput], *, marketplace="demo_tr") -> list[LineResult]:
    if not lines or len({line.line_number for line in lines}) != len(lines):
        raise ValueError("Sipariş boş veya satır numaraları tekrarlı")
    if len({(line.currency, line.exchange_rate) for line in lines}) != 1:
        raise ValueError("Bir siparişin para birimi ve kuru aynı olmalı")
    return _calculate(sorted(lines, key=lambda line: line.line_number), marketplace)


def _calculate(lines, marketplace):
    for line in lines:
        line.validate()
        if marketplace == "demo_tr" and line.currency != "TRY":
            raise ValueError("Demo TRY mağazasında yabancı para kullanılamaz")
    original = [
        _round_half_up(
            (Fraction(line.unit_price_gross) * line.quantity - Fraction(line.seller_discount))
            * Fraction(line.exchange_rate)
            * 100
        )
        for line in lines
    ]
    weights = (
        [Fraction(value) for value in original]
        if sum(original)
        else [Fraction(line.quantity) for line in lines]
    )
    desi = sum(max(Fraction(line.desi), Fraction(line.weight_kg)) * line.quantity for line in lines)
    freight = _shipping_cents(Fraction(sum(original), 100), desi, marketplace)
    outbound = _allocate_integer_cents(freight, weights)
    service = _allocate_integer_cents(0 if marketplace == "amazon_demo" else 1000, weights)
    return_weights = [
        Fraction(gross * line.returned_quantity, line.quantity)
        for gross, line in zip(original, lines, strict=True)
    ]
    if not sum(return_weights):
        return_weights = [Fraction(line.returned_quantity) for line in lines]
    inbound = (
        _allocate_integer_cents(freight, return_weights)
        if sum(return_weights)
        else [0] * len(lines)
    )
    results = []
    for index, line in enumerate(lines):
        remaining = line.quantity - line.returned_quantity
        gross = _round_half_up(Fraction(original[index] * remaining, line.quantity))
        net = _round_half_up(Fraction(gross) / (1 + Fraction(line.vat_percent) / 100))
        commission = _round_half_up(Fraction(gross) * Fraction(line.commission_percent) / 100)
        shipping = outbound[index] + inbound[index]
        fee = _round_half_up(Fraction(service[index] * remaining, line.quantity))
        cost = _round_half_up(
            Fraction(line.unit_cost_net) * remaining * Fraction(line.exchange_rate) * 100
        )
        withholding = _round_half_up(Fraction(net, 100))
        fee_vat = sum(_round_half_up(Fraction(item, 5)) for item in (commission, shipping, fee))
        results.append(
            LineResult(
                line_number=line.line_number,
                gross_sales=_decimal_from_coefficient(gross),
                net_sales=_decimal_from_coefficient(net),
                commission=_decimal_from_coefficient(commission),
                shipping=_decimal_from_coefficient(shipping),
                service=_decimal_from_coefficient(fee),
                cost=_decimal_from_coefficient(cost),
                withholding=_decimal_from_coefficient(withholding),
                profit=_decimal_from_coefficient(net - commission - shipping - fee - cost),
                payout=_decimal_from_coefficient(
                    gross - commission - shipping - fee - fee_vat - withholding
                ),
                sales_vat=_decimal_from_coefficient(gross - net),
                fee_vat=_decimal_from_coefficient(fee_vat),
                cost_vat=_decimal_from_coefficient(
                    _round_half_up(Fraction(cost) * Fraction(line.cost_vat_percent) / 100)
                ),
            )
        )
    return results
