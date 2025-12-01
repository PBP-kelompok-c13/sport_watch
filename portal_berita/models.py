import uuid
from django.db import models
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()

REACTION_CHOICES = [
    ("like", "Like"),
    ("love", "Love"),
    ("fire", "Fire"),
    ("wow", "Wow"),
    ("sad", "Sad"),
]

REACTION_EMOJI_MAP = {
    "like": "\U0001F44D",  # 👍
    "love": "\U00002764\U0000FE0F",  # ❤️
    "fire": "\U0001F525",  # 🔥
    "wow": "\U0001F62E",  # 😮
    "sad": "\U0001F622",  # 😢
}

class KategoriBerita(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nama"]
        verbose_name_plural = "Kategori Berita"

    def __str__(self):
        return self.nama

    def get_category_class(self):
        """Returns a slugified version of the category name for use as a CSS class."""
        return slugify(self.nama)


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
    tanggal_dibuat = models.DateTimeField(default=timezone.now)
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

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def reaction_counts(self):
        counts = {key: 0 for key, _ in REACTION_CHOICES}
        if (
            hasattr(self, "_prefetched_objects_cache")
            and "reactions" in self._prefetched_objects_cache
        ):
            for reaction in self.reactions.all():
                counts[reaction.reaction_type] += 1
        else:
            aggregated = (
                self.reactions.values("reaction_type")
                .annotate(total=Count("reaction_type"))
            )
            for item in aggregated:
                counts[item["reaction_type"]] = item["total"]
        return counts

    @property
    def reaction_summary(self):
        counts = self.reaction_counts
        return [
            {
                "key": key,
                "label": label,
                "emoji": REACTION_EMOJI_MAP.get(key, ""),
                "count": counts.get(key, 0),
            }
            for key, label in REACTION_CHOICES
        ]

    def get_user_reaction(self, user):
        if not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        if reaction:
            return reaction.reaction_type
        return None


class Comment(models.Model):
    berita = models.ForeignKey(Berita, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.berita}'


class NewsReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    berita = models.ForeignKey(Berita, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['berita', 'user'],
                name='unique_user_news_reaction',
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} reacted {self.reaction_type} to {self.berita}'
