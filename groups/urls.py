from django.urls import path
from .views import groups, group, topics

urlpatterns = [
    path('<int:group_id>/topics/', topics),
    path('<int:group_id>', group),
    path('', groups)
]