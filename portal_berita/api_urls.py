from django.urls import path

from . import views

app_name = "portal_berita_api"

urlpatterns = [
    path("news/", views.news_list_json, name="news_list"),
    path("news/load-more/", views.load_more_news, name="news_load_more"),
    path("news/<uuid:id>/", views.berita_json_view, name="news_detail"),
    path("news/<uuid:id>/react/", views.react_to_news, name="news_react"),
    path("news/create/", views.create_news_flutter, name="news_create"),
    path("news/<uuid:id>/edit/", views.edit_news_flutter, name="news_edit"),
    path("news/<uuid:id>/delete/", views.delete_news_flutter, name="news_delete"),
]
