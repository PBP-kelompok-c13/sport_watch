import json
from django.core.management.base import BaseCommand
from shop.models import Product, Category, Brand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from decimal import Decimal

class Command(BaseCommand):
    help = 'Imports product data from a JSON file into the Product model.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing product data.')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(username='admin') # Or use an existing user

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {json_file_path}"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"Invalid JSON in file: {json_file_path}"))
            return

        # Get or create default category and brand
        default_category, _ = Category.objects.get_or_create(name='Scraped Products', defaults={'slug': 'scraped-products'})
        default_brand, _ = Brand.objects.get_or_create(name='Unknown Brand', defaults={'slug': 'unknown-brand'})

        for item in products_data:
            name = item.get('name', 'Unknown Product')
            if not name or name == 'Unknown Product':
                continue

            price_val = item.get('price', '0')
            image_url = item.get('image_url', '')
            product_url = item.get('product_url', '')

            try:
                # Clean and convert price to Decimal
                price_str = str(price_val)
                price = Decimal(price_str.replace('Rp.', '').replace('.', '').strip())
            except (ValueError, TypeError):
                price = Decimal('0.00')

            if price == Decimal('0.00'):
                continue

            # Attempt to infer brand from product name
            brand_name_inferred = "Unknown Brand"
            if "Nike" in name:
                brand_name_inferred = "Nike"
            elif "Adidas" in name:
                brand_name_inferred = "Adidas"
            elif "New Balance" in name:
                brand_name_inferred = "New Balance"
            elif "Puma" in name:
                brand_name_inferred = "Puma"
            elif "Converse" in name:
                brand_name_inferred = "Converse"
            elif "Vans" in name:
                brand_name_inferred = "Vans"
            elif "Crocs" in name:
                brand_name_inferred = "Crocs"
            elif "Asics" in name:
                brand_name_inferred = "Asics"
            
            product_brand, _ = Brand.objects.get_or_create(name=brand_name_inferred, defaults={'slug': slugify(brand_name_inferred)})
            
            # Create or update the Product object
            Product.objects.update_or_create(
                name=name,
                defaults={
                    'price': price,
                    'thumbnail': image_url,
                    'description': f"Original Product URL: {product_url}",
                    'category': default_category, 
                    'brand': product_brand, 
                    'created_by': admin_user,
                    'stock': 10, # Default stock
                    'is_featured': False,
                    'status': 'active',
                    'currency': 'IDR',
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Imported/Updated product: {name}"))

        self.stdout.write(self.style.SUCCESS("Product import complete."))
