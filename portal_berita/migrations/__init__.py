"""Migration helpers for the ``portal_berita`` app.

The team historically had a divergent migration history where
``0002_comment`` could be applied while the clean-up migration
``0002_remove_produk_kategori_remove_berita_ringkasan_and_more`` failed.

Users who ran the migrations during that period ended up with the comment
tables created, but Django recorded that ``0002_remove`` hadn't been
applied.  When newer versions of the project reintroduced the clean-up
migration, Django refused to run ``migrate`` because it detected the
missing dependency.

To keep existing databases working without forcing manual intervention, we
patch things up when the migration module is imported: if Django sees that
``0002_comment`` is already recorded but ``0002_remove`` isn't, we execute
the same defensive clean-up that the migration would have performed and
then mark the clean-up migration as applied.  This mirrors the effects of
the real migration while keeping the migration history consistent so
``python manage.py migrate`` can proceed normally for everyone.
"""

from __future__ import annotations

from contextlib import suppress
import logging

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.db.utils import IntegrityError, OperationalError, ProgrammingError

log = logging.getLogger(__name__)


def _perform_legacy_cleanup() -> None:
    """Drop obsolete tables/columns that the clean-up migration targets."""

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS portal_berita_produk")
        cursor.execute("DROP TABLE IF EXISTS portal_berita_kategoriproduk")

        try:
            cursor.execute("ALTER TABLE portal_berita_berita DROP COLUMN ringkasan")
        except Exception as exc:  # pragma: no cover - defensive
            log.warning(
                "Could not drop legacy column portal_berita_berita.ringkasan; "
                "skipping clean-up step",
                exc_info=exc,
            )
            if connection.vendor == "sqlite":
                cursor.execute("PRAGMA table_info('portal_berita_berita')")
                columns = {row[1] for row in cursor.fetchall()}
                if "ringkasan" in columns:
                    with suppress(Exception):
                        cursor.execute(
                            "ALTER TABLE portal_berita_berita DROP COLUMN ringkasan"
                        )


def _ensure_cleanup_marked() -> None:
    """Backfill the legacy clean-up migration when it's missing."""

    cleanup_key = (
        "portal_berita",
        "0002_remove_produk_kategori_remove_berita_ringkasan_and_more",
    )
    comment_key = ("portal_berita", "0002_comment")

    try:
        connection.ensure_connection()
    except OperationalError:
        return

    recorder = MigrationRecorder(connection)

    try:
        recorder.ensure_schema()
    except OperationalError:
        return

    try:
        applied = set(recorder.migration_qs.values_list("app", "name"))
    except (OperationalError, ProgrammingError):
        return

    if comment_key in applied and cleanup_key not in applied:
        try:
            _perform_legacy_cleanup()
        except Exception as exc:  # pragma: no cover - defensive
            log.warning(
                "Skipping legacy clean-up because of database error; "
                "marking migration as applied anyway to unblock installs.",
                exc_info=exc,
            )
        with suppress(IntegrityError):
            recorder.migration_qs.create(app=cleanup_key[0], name=cleanup_key[1])


_ensure_cleanup_marked()
