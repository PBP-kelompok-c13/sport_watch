from django.urls import path
from portal_berita.views import portalnews_info

app_name = 'portal_berita'

urlpatterns = [
	path('', portalnews_info, name='portalnews_info')
]
