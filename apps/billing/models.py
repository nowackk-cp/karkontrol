from django.conf import settings
from django.db import models


class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(
        max_length=10, choices=[("free", "Ücretsiz"), ("pro", "Demo Pro")], default="free"
    )


class PaymentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    idempotency_key = models.UUIDField()
    outcome = models.CharField(
        max_length=10,
        choices=[("success", "Başarılı"), ("failed", "Reddedildi"), ("timeout", "Zaman aşımı")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"], name="payment_user_key_unique"
            )
        ]
