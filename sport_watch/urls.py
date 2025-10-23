from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal_berita.urls')),
    path('scoreboard/', include('scoreboard.urls')), 
    path("shop/", include("shop.urls")),
    path('fitur_belanja/', include('fitur_belanja.urls')), 
]
