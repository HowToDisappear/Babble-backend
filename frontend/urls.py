from django.urls import path
from .views import ui_app


urlpatterns = [
    path('', ui_app),
]
