from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view


@ensure_csrf_cookie
@api_view(['GET'])
def ui_app(request):
    return render(request, 'index.html', {})
