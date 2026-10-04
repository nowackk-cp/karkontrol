"""Kurallar: docs/KURALLAR.md."""

from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction

ZERO = Decimal("0.00")
CENT = Decimal("0.01")
HUNDRED = Decimal("100")
VERSION = "demo-v1"


def money(value: Decimal) -> Decimal:
    rounded = value.quantize(CENT, rounding=ROUND_HALF_UP)
    return ZERO if rounded == ZERO else rounded


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
        if self.seller_discount + self.platform_coupon > self.unit_price_gross * self.quantity:
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
        return (
            self.payout
            - self.cost
            - self.cost_vat
            - (self.sales_vat - self.fee_vat - self.cost_vat)
            + self.withholding
        )


def allocate(total: Decimal, weights: list[Decimal]) -> list[Decimal]:
    """Kuruşların tamamını korur; eşit kalanlarda liste sırası belirleyicidir."""
    if not weights:
        raise ValueError("Dağıtım ağırlıkları geçersiz")
    for weight in weights:
        validate_decimal(weight, "weight")
    validate_decimal(total, "total")
    if sum(weights) == ZERO:
        weights = [Decimal("1")] * len(weights)
    cents = int(money(total) * HUNDRED)
    return _allocate_cents(cents, [Fraction(weight) for weight in weights])


def _allocate_cents(cents: int, exact_weights: list[Fraction]) -> list[Decimal]:
    # Decimal bölmesi aynı rasyonel kalana farklı son basamaklar verebilir.
    # Fraction ve divmod, eşit kalanları context precision'dan bağımsız tutar.
    weight_sum = sum(exact_weights)
    shares = [divmod(cents * weight, weight_sum) for weight in exact_weights]
    base = [quotient for quotient, _ in shares]
    ranked = sorted(range(len(base)), key=lambda i: (-shares[i][1], i))
    for index in ranked[: cents - sum(base)]:
        base[index] += 1
    return [money(Decimal(value) / HUNDRED) for value in base]


def shipping_fee(gross: Decimal, desi: Decimal, *, marketplace="demo_tr") -> Decimal:
    validate_decimal(gross, "gross")
    validate_decimal(desi, "desi")
    if marketplace == "amazon_demo":
        return Decimal("80.00")
    if marketplace != "demo_tr":
        raise ValueError("Pazaryeri desteklenmiyor")
    base = (
        Decimal("30")
        if gross <= Decimal("300")
        else (Decimal("60") if gross <= Decimal("600") else Decimal("80"))
    )
    units = desi.to_integral_value(rounding=ROUND_CEILING)
    return money(base + max(ZERO, units - Decimal("3")) * Decimal("5"))


def calculate_order(lines: list[LineInput], *, marketplace="demo_tr") -> list[LineResult]:
    if not lines or len({line.line_number for line in lines}) != len(lines):
        raise ValueError("Sipariş boş veya satır numaraları tekrarlı")
    if len({(line.currency, line.exchange_rate) for line in lines}) != 1:
        raise ValueError("Bir siparişin para birimi ve kuru aynı olmalı")
    with localcontext() as context:
        context.prec = 50
        return _calculate(sorted(lines, key=lambda line: line.line_number), marketplace)


def _calculate(lines, marketplace):
    for line in lines:
        line.validate()
        if marketplace == "demo_tr" and line.currency != "TRY":
            raise ValueError("Demo TRY mağazasında yabancı para kullanılamaz")
    original = [
        money((line.unit_price_gross * line.quantity - line.seller_discount) * line.exchange_rate)
        for line in lines
    ]
    weights = original if sum(original) else [Decimal(line.quantity) for line in lines]
    desi = sum(max(line.desi, line.weight_kg) * line.quantity for line in lines)
    freight = shipping_fee(sum(original), desi, marketplace=marketplace)
    outbound = allocate(freight, weights)
    service = allocate(Decimal("0") if marketplace == "amazon_demo" else Decimal("10"), weights)
    return_weights = [
        Fraction(gross) * line.returned_quantity / line.quantity
        for gross, line in zip(original, lines, strict=True)
    ]
    if not sum(return_weights):
        return_weights = [Fraction(line.returned_quantity) for line in lines]
    inbound = (
        _allocate_cents(int(freight * HUNDRED), return_weights)
        if sum(return_weights)
        else [ZERO] * len(lines)
    )
    results = []
    for index, line in enumerate(lines):
        remaining = line.quantity - line.returned_quantity
        gross = money(original[index] * remaining / line.quantity)
        net = money(gross / (Decimal("1") + line.vat_percent / HUNDRED))
        commission = money(gross * line.commission_percent / HUNDRED)
        shipping = outbound[index] + inbound[index]
        fee = money(service[index] * remaining / line.quantity)
        cost = money(line.unit_cost_net * remaining * line.exchange_rate)
        withholding = money(net / HUNDRED)
        fee_vat = sum(money(item * Decimal("0.20")) for item in (commission, shipping, fee))
        results.append(
            LineResult(
                line_number=line.line_number,
                gross_sales=gross,
                net_sales=net,
                commission=commission,
                shipping=shipping,
                service=fee,
                cost=cost,
                withholding=withholding,
                profit=net - commission - shipping - fee - cost,
                payout=gross - commission - shipping - fee - fee_vat - withholding,
                sales_vat=gross - net,
                fee_vat=fee_vat,
                cost_vat=money(cost * line.cost_vat_percent / HUNDRED),
            )
        )
    return results
