from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.order_list, name="list"),
    path("upload/", views.order_upload, name="upload"),
    path("sample/", views.sample_file, name="sample"),
    path("<int:pk>/return/", views.order_return, name="return"),
]
