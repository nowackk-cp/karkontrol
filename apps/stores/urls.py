from django.urls import path

from . import views

app_name = "stores"
urlpatterns = [
    path("", views.store_list, name="list"),
    path("new/", views.store_create, name="create"),
]
