from django.urls import path
from . import views

app_name = 'fitur_belanja'

urlpatterns = [
    path('shopping/', views.shopping_view, name='shopping'),
]
