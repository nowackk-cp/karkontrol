from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", views.order_list, name="list"),
    path("upload/", views.order_upload, name="upload"),
    path("sample/", views.sample_file, name="sample"),
    path("imports/<int:batch_pk>/undo/", views.import_undo, name="undo"),
    path("<int:pk>/return/", views.order_return, name="return"),
]
