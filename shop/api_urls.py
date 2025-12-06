from django.urls import path

from authentication.views import proxy_image
from . import views

app_name = "shop_api"

urlpatterns = [
    path("products/", views.products_json, name="products"),
    path("products/create/", views.create_product_flutter, name="product_create"),
    path("products/<slug:slug>/", views.product_detail_json, name="product_detail"),
    path("products/<uuid:pk>/mini/", views.product_mini_json, name="product_mini"),
    path("products/<uuid:pk>/edit/", views.edit_product_flutter, name="product_edit"),
    path("products/<uuid:pk>/delete/", views.product_delete_flutter, name="product_delete"),
    path("reviews/<uuid:product_id>/", views.reviews_json, name="reviews"),
    path("reviews/<uuid:product_id>/create/", views.create_review, name="review_create"),
    path(
        "reviews/<uuid:product_id>/create-flutter/",
        views.create_review_flutter,
        name="review_create_flutter",
    ),
    path("categories/", views.categories_json, name="categories"),
    path("brands/", views.brands_json, name="brands"),
    path("proxy-image/", proxy_image, name="proxy_image"),
]
