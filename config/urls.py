from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from config.accounts import signup
from config.security import RateLimitedLoginView
from config.views import health, home

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("stores/", include("apps.stores.urls")),
    path("stores/<int:store_pk>/orders/", include("apps.orders.urls")),
    path("stores/<int:store_pk>/reports/", include("apps.reports.urls")),
    path("stores/<int:store_pk>/assistant/", include("apps.assistant.urls")),
    path("subscription/", include("apps.billing.urls")),
    path("accounts/login/", RateLimitedLoginView.as_view(), name="login"),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
