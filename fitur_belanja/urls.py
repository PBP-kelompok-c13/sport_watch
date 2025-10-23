from django.urls import path
from . import views

app_name = "fitur_belanja"

urlpatterns = [
    path("", views.shopping, name="shopping"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("remove/<uuid:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
]
