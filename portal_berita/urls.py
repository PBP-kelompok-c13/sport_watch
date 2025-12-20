from django.urls import path

from portal_berita import views

app_name = "portal_berita"

urlpatterns = [
    path("", views.list_news, name="list_news"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("news/", views.list_news),
    path("news/manage/", views.news_management, name="news_management"),
    path("news/create/", views.create_news, name="create_news"),
    path("category/add/", views.add_category, name="add_category"),
    path("news/<uuid:id>/", views.detail_news, name="detail_news"),
    path("news/<uuid:id>/edit/", views.edit_news, name="edit_news"),
    path("news/<uuid:id>/delete/", views.delete_news, name="delete_news"),
    path("news/<uuid:id>/react/", views.react_to_news, name="react_to_news"),
    path("news/json/<uuid:id>/", views.berita_json_view, name="berita_json_view"),
    path("news/load_more/", views.load_more_news, name="load_more_news"),
]
