from django.urls import path
from . import views

app_name = 'scoreboard'

urlpatterns = [
    path('', views.index, name='index'),

    # admin custom
    path('admin/', views.scoreboard_management, name='scoreboard_management'),
    path('admin/create/', views.create_score, name='create_score'),
    path('admin/edit/<int:pk>/', views.edit_score, name='edit_score'),
    path('admin/delete/<int:pk>/', views.delete_score, name='delete_score'),
    path('filter/', views.filter_scores, name='filter_scores'),
    
    # flutter
    path('api/create-flutter/', views.create_score_flutter, name='create_score_flutter'),
    path('api/edit-flutter/<int:pk>/', views.edit_score_flutter, name='edit_score_flutter'),
    path('api/delete-flutter/<int:pk>/', views.delete_score_flutter, name='delete_score_flutter'),
]
