from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def drop_legacy_structures(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS portal_berita_produk")
        cursor.execute("DROP TABLE IF EXISTS portal_berita_kategoriproduk")
        try:
            cursor.execute("ALTER TABLE portal_berita_berita DROP COLUMN ringkasan")
        except Exception:
            if schema_editor.connection.vendor == "sqlite":
                cursor.execute("PRAGMA table_info('portal_berita_berita')")
                columns = {row[1] for row in cursor.fetchall()}
                if "ringkasan" in columns:
                    try:
                        cursor.execute(
                            "ALTER TABLE portal_berita_berita DROP COLUMN ringkasan"
                        )
                    except Exception:
                        pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    replaces = [
        ("portal_berita", "0002_comment"),
        ("portal_berita", "0003_alter_berita_kategori"),
        ("portal_berita", "0002_remove_produk_kategori_remove_berita_ringkasan_and_more"),
        ("portal_berita", "0004_merge_comment_cleanup"),
    ]

    dependencies = [
        ("portal_berita", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "berita",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="portal_berita.berita",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="portal_berita.comment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.RunPython(drop_legacy_structures, noop),
        migrations.AlterField(
            model_name="berita",
            name="kategori",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="berita",
                to="portal_berita.kategoriberita",
            ),
        ),
    ]
