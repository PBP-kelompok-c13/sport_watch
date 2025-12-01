from django.urls import path
from .views import hello_world, register_user, api_login

urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
    path('register/', register_user, name='register'),
    path('login/', api_login, name='login'),
]
