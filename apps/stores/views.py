from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import StoreForm
from .models import Store


def owned_store(user, pk):
    return get_object_or_404(Store, pk=pk, owner=user)


def store_owner_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        request.karkontrol_store = owned_store(request.user, kwargs["store_pk"])
        return view(request, *args, **kwargs)

    return wrapped


@login_required
@require_safe
def store_list(request):
    return render(request, "stores/list.html", {"stores": Store.objects.filter(owner=request.user)})


@login_required
@require_http_methods(["GET", "POST"])
def store_create(request):
    form = StoreForm(request.POST if request.method == "POST" else None, owner=request.user)
    if request.method == "POST" and form.is_valid():
        store = form.save()
        messages.success(request, "Mağazanız oluşturuldu.")
        return redirect("orders:list", store_pk=store.pk)
    return render(request, "stores/form.html", {"form": form})
