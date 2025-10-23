# from django.urls import path
# from . import views

# app_name = 'fitur_belanja'

# urlpatterns = [
#     path('shopping/', views.shopping_view, name='shopping'),
#     path('add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
#     path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
#     path('', views.index, name='fitur_belanja_index'),
# ]

from django.urls import path
from . import views

app_name = 'fitur_belanja'

urlpatterns = [
    path('', views.shopping_view, name='shopping'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
]

