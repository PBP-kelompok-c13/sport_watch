from django.urls import path

from authentication.views import proxy_image



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
    path(
        "api/reviews/<uuid:product_id>/create-flutter/",
        views.create_review_flutter,
        name="create_review_flutter",
    ),

    path("api/products/<uuid:pk>/delete-flutter/", views.product_delete_flutter, name="product_delete_flutter"),
     path(
        "api/products/<uuid:pk>/edit-flutter/",
        views.edit_product_flutter,          # ← PAKAI YANG INI
        name="edit_product_flutter",
    ),

    #AJAX
    path("create/", views.product_create, name="create"),
    path("<uuid:pk>/edit/", views.product_edit, name="edit"),

    #path("create/", views.create_product, name="create"),
    path("<uuid:pk>/delete/", views.product_delete, name="delete"),


    # STAFFONLY MANAGEMENT 
     path("manage/", views.manage_shop, name="manage_shop"),

    # Kelola Products 
    path("manage/products/", views.manage_products, name="manage_products"),
    path("manage/products/create/", views.admin_product_create, name="admin_product_create"),
    path("manage/products/<uuid:pk>/edit/", views.admin_product_edit, name="admin_product_edit"),
    path("manage/products/<uuid:pk>/delete/", views.admin_product_delete, name="admin_product_delete"),

    # Kelola Brands
    path("manage/brands/<uuid:pk>/edit/", views.brand_edit, name="brand_edit"),
    path("manage/brands/<uuid:pk>/delete/", views.brand_delete, name="brand_delete"),

    # Kelola Cat
    path("manage/categories/<uuid:pk>/edit/", views.category_edit, name="category_edit"),
    path("manage/categories/<uuid:pk>/delete/", views.category_delete, name="category_delete"),

    # Kelola Rev
    path("manage/reviews/<uuid:pk>/delete/", views.review_delete, name="review_delete"),

    #json 
    path('json/', views.show_json, name='show_json'),
    path("api/create-flutter/", views.create_product_flutter, name="create_product_flutter"),
    path("proxy-image/", proxy_image, name="proxy_image"),

    path("api/categories/", views.categories_json, name="categories_json"),
    path("api/brands/", views.brands_json, name="brands_json"),

]
