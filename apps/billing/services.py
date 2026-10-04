from django.db import transaction

from apps.orders.models import OrderLine

from .models import PaymentAttempt, Subscription

FREE_LIMIT = 100


def check_import_limit(user):
    from apps.orders.importing import ImportValidationError

    sub, _ = Subscription.objects.get_or_create(user=user)
    sub = Subscription.objects.select_for_update().get(pk=sub.pk)
    if sub.plan == "free" and OrderLine.objects.filter(store__owner=user).count() > FREE_LIMIT:
        raise ImportValidationError(
            "Ücretsiz plan 100 satırla sınırlı. Abonelik sayfasından Demo Pro'ya geçin."
        )


@transaction.atomic
def demo_payment(user, key, outcome):
    if outcome not in {"success", "failed", "timeout"}:
        raise ValueError("Geçersiz demo ödeme sonucu")
    sub, _ = Subscription.objects.get_or_create(user=user)
    sub = Subscription.objects.select_for_update().get(pk=sub.pk)
    attempt, created = PaymentAttempt.objects.get_or_create(
        user=user,
        idempotency_key=key,
        defaults={"outcome": outcome},
    )
    if created and outcome == "success":
        sub.plan = "pro"
        sub.save(update_fields=["plan"])
    return attempt
