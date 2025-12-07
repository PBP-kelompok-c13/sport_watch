from django.urls import path
from . import api_views

app_name = "portal_berita_api"

urlpatterns = [
    path("news/", api_views.BeritaListCreate.as_view(), name="news_list"),
    path("news/<uuid:id>/", api_views.BeritaDetail.as_view(), name="news_detail"),
    path("news/<uuid:id>/react/", api_views.react_to_news, name="news_react"),
]
