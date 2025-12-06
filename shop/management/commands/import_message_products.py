import json
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from shop.models import Brand, Category, Product


class Command(BaseCommand):
    help = "Import shop products from message.txt-style JSON payloads"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="shop/fixtures/message.json",
            help="Path to the JSON file (default: shop/fixtures/message.json)",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in {path}: {exc}") from exc

        User = get_user_model()

        created_count = 0
        updated_count = 0
        skipped_count = 0

        def _as_decimal(value):
            if value in (None, ""):
                return None
            try:
                return Decimal(str(value))
            except (TypeError, ValueError, ArithmeticError):
                return None

        for entry in data:
            if entry.get("model") != "shop.product":
                skipped_count += 1
                continue

            fields = entry.get("fields", {})
            name = fields.get("name")
            if not name:
                skipped_count += 1
                continue

            category_name = fields.get("category") or "General"
            brand_name = fields.get("brand") or ""
            slug = fields.get("slug") or slugify(name)

            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={"slug": slugify(category_name)},
            )

            brand = None
            if brand_name:
                brand, _ = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={"slug": slugify(brand_name)},
                )

            created_by = None
            created_by_id = fields.get("created_by")
            if created_by_id:
                created_by = User.objects.filter(id=created_by_id).first()

            defaults = {
                "name": name,
                "description": fields.get("description", ""),
                "price": _as_decimal(fields.get("price")) or Decimal("0"),
                "sale_price": _as_decimal(fields.get("sale_price")),
                "currency": (fields.get("currency") or "IDR")[:3],
                "stock": int(fields.get("stock") or 0),
                "total_sold": int(fields.get("total_sold") or 0),
                "thumbnail": fields.get("thumbnail", ""),
                "is_featured": bool(fields.get("is_featured", False)),
                "status": fields.get("status", "active"),
                "rating_avg": float(fields.get("rating_avg") or 0),
                "rating_count": int(fields.get("rating_count") or 0),
                "category": category,
                "brand": brand,
                "created_by": created_by,
            }

            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Products imported. created={created_count}, updated={updated_count}, skipped={skipped_count}"
            )
        )
