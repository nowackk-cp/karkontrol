from django.urls import path

from .views import export_csv, profit_report

app_name = "reports"
urlpatterns = [path("", profit_report, name="profit"), path("export/", export_csv, name="export")]
