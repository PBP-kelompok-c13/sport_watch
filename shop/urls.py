from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("p/<slug:slug>/", views.product_detail, name="detail"),
    # JSON/AJAX endpoints (untuk rubrik Views+JSON)
    path("api/products/", views.products_json, name="products_json"),
    path("api/reviews/<uuid:product_id>/create/", views.create_review, name="create_review"),
]
