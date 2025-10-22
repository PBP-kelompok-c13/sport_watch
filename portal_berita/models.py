import uuid
from django.db import models
from django.contrib.auth import get_user_model

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
    konten = models.TextField()
    kategori = models.ForeignKey(
        KategoriBerita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        self.refresh_from_db(fields=["views"])

    @property
    def berita_hot(self):
        return self.views >= 100
