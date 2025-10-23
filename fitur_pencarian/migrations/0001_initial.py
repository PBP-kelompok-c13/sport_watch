import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal_berita", "0003_alter_berita_kategori"),
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchPreference",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        primary_key=True, default=uuid.uuid4, editable=False, serialize=False
                    ),
                ),
                ("label", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "default_scope",
                    models.CharField(
                        choices=[
                            ("all", "Semua Konten"),
                            ("news", "Berita"),
                            ("products", "Produk"),
                        ],
                        default="all",
                        max_length=20,
                    ),
                ),
                (
                    "min_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
                (
                    "max_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
                ("only_discount", models.BooleanField(default=False)),
                (
                    "is_public",
                    models.BooleanField(
                        default=True,
                        help_text="Jika dicentang, preset dapat digunakan oleh pengguna lain",
                    ),
                ),
                (
                    "role_visibility",
                    models.CharField(
                        choices=[("all", "Semua Pengguna"), ("staff", "Staf Saja")],
                        default="all",
                        max_length=20,
                    ),
                ),
                (
                    "default_brand",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="search_preferences",
                        to="shop.brand",
                    ),
                ),
                (
                    "default_news_category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="search_preferences",
                        to="portal_berita.kategoriberita",
                    ),
                ),
                (
                    "default_product_category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="search_preferences",
                        to="shop.category",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="search_preferences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["label"],
                "unique_together": {("user", "label")},
            },
        ),
        migrations.CreateModel(
            name="SearchLog",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        primary_key=True, default=uuid.uuid4, editable=False, serialize=False
                    ),
                ),
                ("session_key", models.CharField(blank=True, max_length=40)),
                ("keyword", models.CharField(max_length=255)),
                (
                    "scope",
                    models.CharField(
                        choices=[
                            ("all", "Semua Konten"),
                            ("news", "Berita"),
                            ("products", "Produk"),
                        ],
                        default="all",
                        max_length=20,
                    ),
                ),
                ("result_count", models.PositiveIntegerField(default=0)),
                (
                    "preference",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="logs",
                        to="fitur_pencarian.searchpreference",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="search_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
