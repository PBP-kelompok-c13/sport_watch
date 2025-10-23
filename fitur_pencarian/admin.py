from django.contrib import admin

from .models import SearchPreference, SearchLog


@admin.register(SearchPreference)
class SearchPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "user",
        "default_scope",
        "default_news_category",
        "default_product_category",
        "default_brand",
        "only_discount",
        "role_visibility",
        "is_public",
        "updated_at",
    )
    list_filter = (
        "default_scope",
        "role_visibility",
        "only_discount",
        "is_public",
    )
    search_fields = ("label", "description", "user__username")
    autocomplete_fields = ("user",)
    raw_id_fields = (
        "default_news_category",
        "default_product_category",
        "default_brand",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "label",
                    "description",
                    "default_scope",
                    "role_visibility",
                    "is_public",
                )
            },
        ),
        (
            "Filter bawaan",
            {
                "fields": (
                    "default_news_category",
                    "default_product_category",
                    "default_brand",
                    "min_price",
                    "max_price",
                    "only_discount",
                )
            },
        ),
        ("Meta", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = (
        "keyword",
        "scope",
        "user",
        "preference",
        "result_count",
        "created_at",
    )
    list_filter = ("scope", "created_at")
    search_fields = ("keyword", "user__username")
    autocomplete_fields = ("user", "preference")
    readonly_fields = ("created_at", "updated_at")
