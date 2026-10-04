from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.stores.models import Store

from .search import product_search_text


def money_field(label):
    return models.DecimalField(
        label,
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )


class OrderLine(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="order_lines")
    import_batch = models.ForeignKey(
        "ImportBatch", on_delete=models.RESTRICT, related_name="lines", null=True, blank=True
    )
    order_number = models.CharField("Sipariş no", max_length=64)
    line_number = models.PositiveIntegerField("Satır no", validators=[MinValueValidator(1)])
    order_date = models.DateField("Sipariş tarihi")
    product_name = models.CharField("Ürün", max_length=200)
    sku = models.CharField("Ürün kodu", max_length=64)
    search_text = models.TextField(editable=False, default="", blank=True)
    quantity = models.PositiveIntegerField("Adet", validators=[MinValueValidator(1)])
    unit_price_gross = money_field("Birim fiyat (KDV dahil)")
    unit_cost_net = money_field("Birim maliyet (KDV hariç)")
    vat_percent = models.DecimalField(
        "KDV (%)",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    commission_percent = models.DecimalField(
        "Komisyon (%)",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    seller_discount = money_field("Satıcı indirimi (satır toplamı)")
    platform_coupon = money_field("Pazaryeri kuponu (satır toplamı)")
    returned_quantity = models.PositiveIntegerField("İade adedi", default=0)
    imported_returned_quantity = models.PositiveIntegerField(
        default=None, null=True, blank=True, editable=False
    )
    desi = money_field("Birim desi")
    weight_kg = money_field("Birim ağırlık (kg)")
    cost_vat_percent = models.DecimalField(
        "Maliyet KDV (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("20"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    currency = models.CharField(
        "Para birimi",
        max_length=3,
        default="TRY",
        choices=[
            ("TRY", "TRY"),
            ("USD", "USD"),
            ("EUR", "EUR"),
        ],
    )
    exchange_rate = models.DecimalField(
        "Sipariş kuru (TRY)",
        max_digits=12,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0.000001"))],
    )

    class Meta:
        ordering = ["-order_date", "order_number", "line_number"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    desi__gte=0,
                    weight_kg__gte=0,
                    cost_vat_percent__gte=0,
                    cost_vat_percent__lte=100,
                    exchange_rate__gt=0,
                    currency__in=["TRY", "USD", "EUR"],
                ),
                name="order_shipping_fx_ranges",
            ),
            models.CheckConstraint(
                condition=~models.Q(currency="TRY") | models.Q(exchange_rate=1),
                name="order_try_exchange_one",
            ),
            models.UniqueConstraint(
                fields=["store", "order_number", "line_number"], name="order_store_line_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1), name="order_quantity_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(line_number__gte=1), name="order_line_positive"
            ),
            models.CheckConstraint(
                condition=models.Q(returned_quantity__lte=models.F("quantity")),
                name="order_return_quantity_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    unit_price_gross__gte=0,
                    unit_cost_net__gte=0,
                    seller_discount__gte=0,
                    platform_coupon__gte=0,
                ),
                name="order_money_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    vat_percent__gte=0,
                    vat_percent__lte=100,
                    commission_percent__gte=0,
                    commission_percent__lte=100,
                ),
                name="order_rates_range",
            ),
        ]

    def clean(self):
        super().clean()
        if self.quantity is not None and self.returned_quantity > self.quantity:
            raise ValidationError({"returned_quantity": "İade adedi sipariş adedini aşamaz."})
        if self.unit_price_gross is not None and self.quantity is not None:
            if self.seller_discount + self.platform_coupon > self.unit_price_gross * self.quantity:
                raise ValidationError("İndirim ve kupon toplamı brüt satır tutarını aşamaz.")
        if self.currency == "TRY" and self.exchange_rate != Decimal("1"):
            raise ValidationError("TRY kuru 1 olmalı.")
        if self.currency != "TRY" and self.store.marketplace != Store.Marketplace.AMAZON:
            raise ValidationError("Yabancı para yalnız Amazon demo mağazasında desteklenir.")

    def save(self, *args, **kwargs):
        self.search_text = product_search_text(self.product_name, self.sku)
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"search_text"}
        return super().save(*args, **kwargs)


class FinancialLine(models.Model):
    """SQL toplamlarında kayan nokta yerine tamsayı kuruş saklayan hesap kaydı."""

    line = models.OneToOneField(OrderLine, on_delete=models.CASCADE, related_name="financial")
    rule_version = models.CharField(max_length=30, default="demo-v1")
    gross_sales = models.BigIntegerField()
    net_sales = models.BigIntegerField()
    commission = models.BigIntegerField()
    shipping = models.BigIntegerField()
    service = models.BigIntegerField()
    cost = models.BigIntegerField()
    withholding = models.BigIntegerField()
    profit = models.BigIntegerField()
    payout = models.BigIntegerField()
    sales_vat = models.BigIntegerField()
    fee_vat = models.BigIntegerField()
    cost_vat = models.BigIntegerField()


class ImportBatch(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="import_batches")
    digest = models.CharField(max_length=64)
    created_lines = models.PositiveIntegerField(default=0)
    skipped_lines = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["store", "digest"], name="import_store_digest_unique")
        ]
