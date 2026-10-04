from django.urls import path

from .views import chat

app_name = "assistant"
urlpatterns = [path("", chat, name="chat")]
