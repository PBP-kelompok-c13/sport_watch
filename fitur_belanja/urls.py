from django.urls import path
from . import views

app_name = "fitur_belanja"

urlpatterns = [
    path("", views.shopping, name="shopping"),
    path("checkout/", views.checkout, name="checkout"),
]
