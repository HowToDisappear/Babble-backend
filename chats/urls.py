from django.urls import path

from .views import direct_messages, group_messages

urlpatterns = [
    path('dm', direct_messages),
    path('gm', group_messages),
]