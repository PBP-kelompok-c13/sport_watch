import uuid
from django.db import models
from django.contrib.auth import get_user_model

"""
MODELS <-<>-> VIEWS <-<>-> TEMPLATES

models.py -> merupakan data & logika bisnis
template.py -> tampilan akhir yang dilihat oleh pengguna
views.pt -> yang menghubungi data (atau model) dan tampilan (template)

class Berita()         ->   berupa id, judul, konten, kategori (dari BeritaKategori()), 
                            thumbnail, views, penulis, sumber, is_published, 
						    tanggal_dibuat, tanggal_diperbarui.
class kategoriBerita() ->   berupa id, nama.

class Produk()         ->   berupa id, nama, deskripsi, kategori (dari ProdukKategori ()), 
                            thumbnail, harga, stok, views, 
							tanggal_ditambahkan, tanggal_diperbarui
class KategoriProduk() ->   berupa id, nama.



"""

User = get_user_model()

class KategoriBerita(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nama"]
        verbose_name_plural = "Kategori Berita"

    def __str__(self):
        return self.nama


class Berita(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    judul = models.CharField(max_length=255, unique=True)
    ringkasan = models.TextField(max_length=500, blank=True)
    konten = models.TextField()
    kategori = models.ForeignKey(
        KategoriBerita,
        on_delete=models.SET_NULL,
        null=True,
        related_name="berita",
    )
    thumbnail = models.URLField(blank=True, null=True)
    views = models.PositiveBigIntegerField(default=0)
    penulis = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="berita",
    )
    sumber = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=False)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-tanggal_dibuat"]

    def __str__(self):
        return self.judul

    def increment_views(self):
        self.views = models.F("views") + 1
        self.save(update_fields=["views"])

    @property
    def berita_hot(self):
        return self.views >= 100

class KategoriProduk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nama"]
        verbose_name_plural = "Kategori Produk"

    def __str__(self):
        return self.nama


class Produk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True)
    kategori = models.ForeignKey(
        KategoriProduk,
        on_delete=models.SET_NULL,
        null=True,
        related_name="produk",
    )
    thumbnail = models.URLField(blank=True, null=True)
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    stok = models.PositiveIntegerField(default=0)
    views = models.PositiveBigIntegerField(default=0)
    tanggal_ditambahkan = models.DateTimeField(auto_now_add=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-tanggal_ditambahkan"]

    def __str__(self):
        return self.nama

    def increment_views(self):
        self.views = models.F("views") + 1
        self.save(update_fields=["views"])

    @property
    def habis_stok(self):
        return self.stok == 0