from django.urls import path
from authentication.views import login, register, proxy_image

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
	path('register/', register, name='register'),
	path('proxy-image/', proxy_image, name='proxy_image'),
]