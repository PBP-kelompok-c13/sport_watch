from django.urls import path, include

urlpatterns = [
    path('', include('portal_berita.urls')),
]