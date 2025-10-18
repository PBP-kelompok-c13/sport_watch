from django.urls import path
from portal_berita import views

app_name = 'portal_berita'

urlpatterns = [
	path('', views.main_view, name='main'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('news/', views.list_news, name='list_news'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/<uuid:id>/', views.detail_news, name='detail_news'),
    path('news/<uuid:id>/edit/', views.edit_news, name='edit_news'),
    path('news/<uuid:id>/delete/', views.delete_news, name='delete_news'),
    path('news/json/', views.berita_json_view, name='berita_json_view'),
]