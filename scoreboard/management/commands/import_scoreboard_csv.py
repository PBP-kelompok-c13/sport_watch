import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from scoreboard.models import Scoreboard


class Command(BaseCommand):
    help = "Import scoreboard rows from a CSV file into the Scoreboard model."

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to the scoreboard CSV file (columns: id,tim1,tim2,skor_tim1,skor_tim2,sport,status,tanggal,logo_tim1,logo_tim2).",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"File not found: {csv_path}")

        required_columns = {
            "tim1",
            "tim2",
            "skor_tim1",
            "skor_tim2",
            "sport",
            "status",
            "tanggal",
        }
        allowed_sports = {code for code, _ in Scoreboard.SPORT_CHOICES}
        allowed_status = {code for code, _ in Scoreboard.STATUS_CHOICES}

        created = 0
        updated = 0
        skipped = 0

        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fieldnames = set(reader.fieldnames or [])

            missing = required_columns - fieldnames
            if missing:
                raise CommandError(f"Missing required columns: {', '.join(sorted(missing))}")

            for row in reader:
                tim1 = (row.get("tim1") or "").strip()
                tim2 = (row.get("tim2") or "").strip()
                if not tim1 or not tim2:
                    skipped += 1
                    continue

                try:
                    skor_tim1 = int(row.get("skor_tim1") or 0)
                    skor_tim2 = int(row.get("skor_tim2") or 0)
                except (TypeError, ValueError):
                    skipped += 1
                    continue

                sport_raw = (row.get("sport") or "").upper()
                sport = sport_raw if sport_raw in allowed_sports else "NBA"

                status_raw = (row.get("status") or "").lower()
                status = "recent" if status_raw == "finished" else status_raw
                status = status if status in allowed_status else "upcoming"

                tanggal_str = (row.get("tanggal") or "").strip()
                tanggal = parse_datetime(tanggal_str)
                if not tanggal:
                    try:
                        tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        tanggal = timezone.now()

                if timezone.is_naive(tanggal):
                    tanggal = timezone.make_aware(tanggal, timezone.get_default_timezone())

                record_defaults = {
                    "tim1": tim1,
                    "tim2": tim2,
                    "skor_tim1": skor_tim1,
                    "skor_tim2": skor_tim2,
                    "sport": sport,
                    "status": status,
                    "tanggal": tanggal,
                    "logo_tim1": (row.get("logo_tim1") or "").strip() or None,
                    "logo_tim2": (row.get("logo_tim2") or "").strip() or None,
                }

                pk_value = row.get("id")
                obj = None
                if pk_value:
                    try:
                        pk_int = int(pk_value)
                    except (TypeError, ValueError):
                        pk_int = None

                    if pk_int:
                        obj, created_flag = Scoreboard.objects.update_or_create(
                            id=pk_int,
                            defaults=record_defaults,
                        )
                        if created_flag:
                            created += 1
                        else:
                            updated += 1
                        continue

                obj = Scoreboard.objects.create(**record_defaults)
                if obj:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Scoreboard import complete. created={created}, updated={updated}, skipped={skipped}"
            )
        )
