
from django.urls import path
from . import views

app_name = "fitur_belanja"

urlpatterns = [
    path("", views.shopping, name="shopping"),          # /cart/
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("update/", views.update_qty, name="update_qty"),
    path("remove/", views.remove_item, name="remove_item"),
]
