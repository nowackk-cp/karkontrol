from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from config.views import health, home

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("stores/", include("apps.stores.urls")),
    path("stores/<int:store_pk>/orders/", include("apps.orders.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
]
