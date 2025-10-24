import uuid
from django.db import models
from django.contrib.auth import get_user_model
from portal_berita.models import KategoriBerita
from shop.models import Category, Brand


User = get_user_model()


class TimeStampedModel(models.Model):
    """Abstract base model that adds created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SearchPreference(TimeStampedModel):
    """Store reusable search presets for each user."""

    class SearchScope(models.TextChoices):
        ALL = "all", "Semua Konten"
        NEWS = "news", "Berita"
        PRODUCTS = "products", "Produk"

    class RoleVisibility(models.TextChoices):
        ALL = "all", "Semua Pengguna"
        STAFF = "staff", "Staf Saja"
        PRIVATE = "private", "Pribadi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="search_preferences"
    )
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_scope = models.CharField(
        max_length=20,
        choices=SearchScope.choices,
        default=SearchScope.ALL,
    )
    default_news_category = models.ForeignKey(
        KategoriBerita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_preferences_news",
    )
    default_product_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_preferences_product",
    )
    default_brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_preferences_brand",
    )
    min_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    only_discount = models.BooleanField(default=False)
    is_public = models.BooleanField(
        default=True,
        help_text="Jika dicentang, preset dapat digunakan oleh pengguna lain",
    )
    role_visibility = models.CharField(
        max_length=20,
        choices=RoleVisibility.choices,
        default=RoleVisibility.ALL,
    )

    class Meta:
        ordering = ["label"]
        unique_together = ("user", "label")

    def __str__(self) -> str:
        return f"{self.label} - {self.user}" if self.user_id else self.label

    @property
    def is_staff_only(self) -> bool:
        return self.role_visibility == self.RoleVisibility.STAFF

    @property
    def is_private(self) -> bool:
        return self.role_visibility == self.RoleVisibility.PRIVATE


class SearchLog(TimeStampedModel):
    """History of searches, used for analytics and recommendations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    session_key = models.CharField(max_length=40, blank=True)
    keyword = models.CharField(max_length=255)
    scope = models.CharField(
        max_length=20,
        choices=SearchPreference.SearchScope.choices,
        default=SearchPreference.SearchScope.ALL,
    )
    preference = models.ForeignKey(
        SearchPreference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    result_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        user = self.user.username if self.user_id else "anon"
        return f"{self.keyword} ({self.scope}) oleh {user}"
