# shop/models.py
import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# Inheritance base
class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedUUIDModel):
    # self-FK untuk kategori bertingkat 
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='children'
    )

    class Meta:
        ordering = ["name"]
        unique_together = (("parent", "slug"),)  
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.full_path

    @property
    def full_path(self) -> str:
        # tampilkan path lengkap
        names, node = [self.name], self.parent
        while node:
            names.append(node.name)
            node = node.parent
        return " / ".join(reversed(names))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(TimeStampedUUIDModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedUUIDModel):
    # relasi dan kepemilikan
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name="products"
    )

    # data utama
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    # harga dan stok
    # DecimalField untuk akurasi harga (best practice)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3, default="IDR")  #Bisa uuid atau idr
    stock = models.PositiveIntegerField(default=0)
    total_sold = models.PositiveIntegerField(default=0)

    # meta dan status
    thumbnail = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    STATUS = (("draft", "Draft"), ("active", "Active"), ("archived", "Archived"))
    status = models.CharField(max_length=10, choices=STATUS, default="active", db_index=True)

    # rating agregat untuk review disimpan cepat
    rating_avg = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    rating_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["name", "category"], name="uniq_product_name_per_category")
        ]
        indexes = [
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name

    # util propertires view dan templatte
    @property
    def final_price(self):
        #kita prioritaskan yang diskon
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def discount_percent(self):
        if self.sale_price is None:
            return 0
        if self.price and self.price > 0:
            return round(100 * (float(self.price - self.sale_price) / float(self.price)))
        return 0

    @property
    def in_stock(self):
        return self.stock > 0 and self.status == "active"

    def reserve(self, qty: int = 1):
        #kurangi stok saat ditambahkan ke keranjang
        if qty < 1:
            raise ValueError("qty harus >= 1")
        if qty > self.stock:
            raise ValueError("stok tidak cukup")
        self.stock -= qty
        self.total_sold += qty
        self.save(update_fields=["stock", "total_sold", "updated_at"])

    def restock(self, qty: int = 1):
        if qty < 1:
            raise ValueError("qty harus >= 1")
        self.stock += qty
        self.save(update_fields=["stock", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            # pastikan unik walau nama sama
            candidate, i = base, 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)


class ProductImage(TimeStampedUUIDModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField()
    alt_text = models.CharField(max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "created_at"]

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(TimeStampedUUIDModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    content = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    #is_featured = 

    class Meta:
        ordering = ["-created_at"]
        unique_together = (("product", "user"),)

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.user}"

    #setelah checkout selesai


# Fitur Pencarian bisa memanfaatkan index di Product(price, status, is_featured) dan field slug/name/brand/category.

# Fitur Belanja  tinggal pakai Product.reserve(qty) saat checkout. atau validasi product.in_stock.