from django.urls import include, path

urlpatterns = [
    # Session-backed auth for mobile/web clients
    path("auth/", include(("authentication.api_urls", "authentication_api"), namespace="auth")),

    # REST-style JSON endpoints
    path("news/", include(("portal_berita.api_urls", "portal_berita_api"), namespace="news")),
    path("scoreboard/", include(("scoreboard.api_urls", "scoreboard_api"), namespace="scoreboard")),
    path("shop/", include(("shop.api_urls", "shop_api"), namespace="shop")),
    path("cart/", include(("fitur_belanja.api_urls", "fitur_belanja_api"), namespace="cart")),
    path("search/", include(("fitur_pencarian.api_urls", "fitur_pencarian_api"), namespace="search")),

    # Existing DRF token endpoints preserved under the same prefix
    path("", include(("api.urls", "legacy_api"), namespace="legacy_api")),
]
