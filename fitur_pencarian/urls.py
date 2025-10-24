from django.urls import path
from . import views

app_name = "fitur_pencarian"

urlpatterns = [
    path("", views.search_page, name="search_page"),
    path("api/results/", views.ajax_search_results, name="ajax_search_results"),
    path("api/preferences/form/", views.ajax_preference_form, name="ajax_preference_form"),
    path("api/preferences/submit/", views.ajax_preference_submit, name="ajax_preference_submit"),
    path("api/preferences/delete/", views.ajax_preference_delete, name="ajax_preference_delete"),
    path("api/preferences/<uuid:id>/form/", views.ajax_preference_form, name="ajax_preference_form_id"),
    path("api/preferences/<uuid:id>/submit/", views.ajax_preference_submit, name="ajax_preference_submit_id"),
    path("api/recent/", views.ajax_recent_searches, name="ajax_recent_searches"),
    path("api/analytics/", views.ajax_search_analytics, name="ajax_search_analytics"),
]
