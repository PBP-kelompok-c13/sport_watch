from django.urls import path

from . import views

app_name = "authentication_api"

urlpatterns = [
    # Session-backed auth endpoints (JSON responses)
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("proxy-image/", views.proxy_image, name="proxy_image"),
]
