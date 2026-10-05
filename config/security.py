"""Bound streamed uploads and authentication attempts before expensive work."""

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.http import HttpResponse
from django.utils.crypto import salted_hmac


class LimitedUploadHandler(FileUploadHandler):
    """Cap total file bytes per request, even when no Content-Length is supplied."""

    def __init__(self, request=None):
        super().__init__(request)
        self.total_bytes = 0

    def receive_data_chunk(self, raw_data, start):
        self.total_bytes += len(raw_data)
        if self.total_bytes > settings.FILE_UPLOAD_MAX_BYTES:
            self.request.karkontrol_upload_too_large = True
            raise StopUpload(connection_reset=False)
        return raw_data

    def file_complete(self, file_size):
        return None


class UploadLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(request, "karkontrol_upload_too_large", False):
            return HttpResponse("Dosya yükleme toplamı en fazla 5 MB olabilir.", status=413)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == "POST" and request.content_type == "multipart/form-data":
            # Complete parsing before the view runs: a small completed first
            # file must never be imported after a later file triggers StopUpload.
            _ = request.FILES
            if getattr(request, "karkontrol_upload_too_large", False):
                return HttpResponse("Dosya yükleme toplamı en fazla 5 MB olabilir.", status=413)
        return None


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["data-testid"] = "login-username"
        self.fields["password"].widget.attrs["data-testid"] = "login-password"


class RateLimitedLoginView(LoginView):
    authentication_form = LoginForm

    def _keys(self):
        # REMOTE_ADDR is supplied by the web server; untrusted forwarded headers
        # must never let callers choose a new rate-limit identity.
        address = self.request.META.get("REMOTE_ADDR", "")
        username = self.request.POST.get("username", "").strip().casefold()
        return [
            "login:pair:" + salted_hmac("login-pair", address + "\0" + username).hexdigest(),
            "login:ip:" + salted_hmac("login-ip", address).hexdigest(),
        ]

    def post(self, request, *args, **kwargs):
        keys = self._keys()
        limits = [settings.LOGIN_RATE_LIMIT_ATTEMPTS, settings.LOGIN_RATE_LIMIT_IP_ATTEMPTS]
        if any(cache.get(key, 0) >= limit for key, limit in zip(keys, limits, strict=True)):
            return self._limited_response()
        # add/incr reserve each attempt atomically on a shared backend. A fresh
        # add also handles expiration between the preflight check and increment.
        for key, limit in zip(keys, limits, strict=True):
            cache.add(key, 0, timeout=settings.LOGIN_RATE_LIMIT_WINDOW)
            try:
                count = cache.incr(key)
            except ValueError:
                cache.add(key, 0, timeout=settings.LOGIN_RATE_LIMIT_WINDOW)
                count = cache.incr(key)
            if count > limit:
                return self._limited_response()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        cache.delete(self._keys()[0])
        return super().form_valid(form)

    def _limited_response(self):
        response = HttpResponse(
            "Çok fazla giriş denemesi. Lütfen daha sonra tekrar deneyin.", status=429
        )
        response["Retry-After"] = str(settings.LOGIN_RATE_LIMIT_WINDOW)
        return response
