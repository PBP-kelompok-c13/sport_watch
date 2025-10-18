from django.urls import path, include

urlpatterns = [
    path('', include('portal_berita.urls')),
    path('scoreboard/', include('scoreboard.urls')), 
]