import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import PaymentAttempt, Subscription
from .services import demo_payment


class DemoPaymentForm(forms.Form):
    key = forms.UUIDField(widget=forms.HiddenInput)
    outcome = forms.ChoiceField(
        label="Sahte ödeme sonucu", choices=PaymentAttempt._meta.get_field("outcome").choices
    )


@login_required
@require_http_methods(["GET", "POST"])
def subscription(request):
    sub, _ = Subscription.objects.get_or_create(user=request.user)
    form = DemoPaymentForm(
        request.POST if request.method == "POST" else None, initial={"key": uuid.uuid4()}
    )
    if request.method == "POST" and form.is_valid():
        attempt = demo_payment(request.user, form.cleaned_data["key"], form.cleaned_data["outcome"])
        text = {
            "success": "Demo Pro etkinleştirildi.",
            "failed": "Sahte ödeme reddedildi. Plan değişmedi.",
            "timeout": "Sahte ödeme zaman aşımına uğradı. Plan değişmedi.",
        }[attempt.outcome]
        messages.info(request, text)
        return redirect("billing:subscription")
    return render(request, "billing/subscription.html", {"subscription": sub, "form": form})
