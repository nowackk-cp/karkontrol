from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.stores.views import store_owner_required

from .llm import ask_llm
from .service import ask


class QuestionForm(forms.Form):
    question = forms.CharField(
        label="Sorunuz",
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3, "data-testid": "assistant-question"}),
    )


@login_required
@store_owner_required
@require_http_methods(["GET", "POST"])
def chat(request, store_pk):
    form = QuestionForm(request.POST if request.method == "POST" else None)
    result = None
    if request.method == "POST" and form.is_valid():
        responder = ask_llm if settings.ASSISTANT_BACKEND == "local" else ask
        result = responder(
            user=request.user, store_pk=store_pk, question=form.cleaned_data["question"]
        )
    return render(
        request,
        "assistant/chat.html",
        {
            "store": request.karkontrol_store,
            "form": form,
            "result": result,
            "llm_enabled": settings.ASSISTANT_BACKEND == "local",
        },
    )
