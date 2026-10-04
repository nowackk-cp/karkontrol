from django.urls import path

from .views import subscription

app_name = "billing"
urlpatterns = [path("", subscription, name="subscription")]
