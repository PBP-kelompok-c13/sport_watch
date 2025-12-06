from django.urls import path

from . import views

app_name = "fitur_pencarian_api"

urlpatterns = [
    path("results/", views.ajax_search_results, name="search_results"),
    path("preferences/form/", views.ajax_preference_form, name="preference_form"),
    path("preferences/submit/", views.ajax_preference_submit, name="preference_submit"),
    path("preferences/delete/", views.ajax_preference_delete, name="preference_delete"),
    path("preferences/<uuid:id>/form/", views.ajax_preference_form, name="preference_form_id"),
    path("preferences/<uuid:id>/submit/", views.ajax_preference_submit, name="preference_submit_id"),
    path("recent/", views.ajax_recent_searches, name="recent_searches"),
    path("analytics/", views.ajax_search_analytics, name="analytics"),
    path("filter-options/", views.ajax_filter_options, name="filter_options"),
]
