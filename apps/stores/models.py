from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Store(models.Model):
    class Marketplace(models.TextChoices):
        DEMO = "demo_tr", "Pazaryeri demo · TRY"
        AMAZON = "amazon_demo", "Amazon demo · TRY / USD / EUR"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField("Mağaza adı", max_length=100)
    marketplace = models.CharField(
        "Pazaryeri", max_length=20, choices=Marketplace, default=Marketplace.DEMO
    )
    commission_percent = models.DecimalField(
        "Varsayılan komisyon (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="store_owner_name_unique"),
            models.CheckConstraint(
                condition=models.Q(commission_percent__gte=0, commission_percent__lte=100),
                name="store_commission_range",
            ),
        ]

    def __str__(self):
        return self.name
