from django.urls import path
from . import views
app_name = "shop"
urlpatterns = [
    path("", views.product_list, name="list"),
    path("p/<slug:slug>/", views.product_detail, name="detail"),
    path("api/products/", views.products_json, name="products_json"),
    path("api/products/<slug:slug>/", views.product_detail_json, name="product_detail_json"),
    path("api/reviews/<uuid:product_id>/", views.reviews_json, name="reviews_json"),
    path("api/reviews/<uuid:product_id>/create/", views.create_review, name="create_review"),
    path("api/products/<uuid:pk>/mini/", views.product_mini_json, name="product_mini_json"),
    path("create/", views.product_create, name="create"),
    path("<uuid:pk>/edit/", views.product_edit, name="edit"),
    path("create/", views.create_product, name="create"),
]
