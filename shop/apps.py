# shop/apps.py
from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    verbose_name = "Shop / Merchandise"

    def ready(self):
        # import di sini agar tidak circular-import saat migrate/startup
        from . import signals  # noqa: F401
