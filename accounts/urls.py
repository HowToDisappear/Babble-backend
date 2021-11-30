from django.urls import path
from .views import signup, activate, update, signin, signout, account, contacts, contact

urlpatterns = [
    path('signup', signup),
    path('activate/<uid>/<token>', activate),
    path('update/<uid>/<token>', update),
    path('signin', signin),
    path('signout', signout),
    path('account', account),
    path('contacts/<int:cont_id>', contact),
    path('contacts', contacts),
]
