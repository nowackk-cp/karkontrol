from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.stores.models import Store


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
    order_number = models.CharField("Sipariş no", max_length=64)
    line_number = models.PositiveIntegerField("Satır no", validators=[MinValueValidator(1)])
    order_date = models.DateField("Sipariş tarihi")
    product_name = models.CharField("Ürün", max_length=200)
    sku = models.CharField("Ürün kodu", max_length=64)
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

    class Meta:
        ordering = ["-order_date", "order_number", "line_number"]
        constraints = [
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
