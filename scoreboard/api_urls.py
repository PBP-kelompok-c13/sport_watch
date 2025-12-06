from django.urls import path

from . import views

app_name = "scoreboard_api"

urlpatterns = [
    path("", views.filter_scores, name="scores"),
    path("create/", views.create_score_flutter, name="create_score"),
    path("<int:pk>/edit/", views.edit_score_flutter, name="edit_score"),
    path("<int:pk>/delete/", views.delete_score_flutter, name="delete_score"),
]
