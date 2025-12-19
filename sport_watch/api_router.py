from django.urls import include, path

urlpatterns = [
    # Session-backed auth for mobile/web clients
    path(
        "auth/",
        include(("authentication.api_urls", "authentication_api"), namespace="api_auth"),
    ),

    # REST-style JSON endpoints
    path(
        "news/",
        include(("portal_berita.api_urls", "portal_berita_api"), namespace="api_news"),
    ),
    path(
        "scoreboard/",
        include(("scoreboard.api_urls", "scoreboard_api"), namespace="api_scoreboard"),
    ),
    path(
        "shop/",
        include(("shop.api_urls", "shop_api"), namespace="api_shop"),
    ),
    path(
        "cart/",
        include(("fitur_belanja.api_urls", "fitur_belanja_api"), namespace="api_cart"),
    ),
    path(
        "search/",
        include(("fitur_pencarian.api_urls", "fitur_pencarian_api"), namespace="api_search"),
    ),
]
