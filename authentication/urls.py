from django.urls import path

from authentication.views import login_user, register_user, logout_user, proxy_image, profile

app_name = 'authentication'

urlpatterns = [
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('logout/', logout_user, name='logout'),
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('profile/', profile, name='profile'),
]
