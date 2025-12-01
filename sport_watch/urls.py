from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal_berita.urls')),
    path('authentication/', include(('authentication.urls', 'authentication'), namespace='authentication')),
    path('auth/', include(('authentication.urls', 'authentication'), namespace='auth_alias')),
    path('scoreboard/', include('scoreboard.urls')),
    path("shop/", include("shop.urls")),
    path('cart/', include(('fitur_belanja.urls', 'fitur_belanja'), namespace='fitur_belanja')),
    path('search/', include(('fitur_pencarian.urls', 'fitur_pencarian'), namespace='fitur_pencarian')),
    path('api/', include('api.urls')),
]
