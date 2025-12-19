from django.urls import path

from . import api_views, views

app_name = "portal_berita_api"

urlpatterns = [
    # Flutter/JSON endpoints
    path("", views.news_list_json, name="news_list_json"),
    path("create-flutter/", views.create_news_flutter, name="create_news_flutter"),
    path("<uuid:id>/edit-flutter/", views.edit_news_flutter, name="edit_news_flutter"),
    path("<uuid:id>/delete-flutter/", views.delete_news_flutter, name="delete_news_flutter"),
    path("<uuid:id>/comments/", views.news_comments_json, name="news_comments_json"),
    path("<uuid:id>/react/", views.react_to_news, name="news_react_json"),
    path("<uuid:id>/comment/create/", views.create_comment_flutter, name="create_comment_flutter"),

    # DRF endpoints (kept for existing integrations)
    path("rest/", api_views.BeritaListCreate.as_view(), name="news_list"),
    path("rest/<uuid:id>/", api_views.BeritaDetail.as_view(), name="news_detail"),
    path("rest/<uuid:id>/react/", api_views.react_to_news, name="news_react"),
]
