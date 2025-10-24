import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Scrapes product data from footlocker.id/nike.html and saves it to a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, help='Path to the output JSON file', default='footlocker_nike.json')

    def handle(self, *args, **options):
        output_file = options['output']
        self.scrape_footlocker_nike(output_file)

    def scrape_footlocker_nike(self, output_file):
        URL = "https://www.footlocker.id/nike.html"
        scraped_data = []

        try:
            page = requests.get(URL)
            page.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error fetching URL: {e}"))
            return

        soup = BeautifulSoup(page.content, "html.parser")

        # Find all product items
        products = soup.find_all("li", class_="product-item")

        if not products:
            self.stdout.write(self.style.ERROR("Could not find any products."))
            return

        for product in products:
            name_element = product.find("a", class_="product-item-link")
            price_element = product.find("span", class_="price")
            image_element = product.find("img", class_="product-image-photo")
            link_element = product.find("a", class_="product-item-photo")

            name = name_element.get_text(strip=True) if name_element else "N/A"
            price = price_element.get_text(strip=True) if price_element else "N/A"
            image_url = image_element['src'] if image_element and 'src' in image_element else "N/A"
            product_url = link_element['href'] if link_element and 'href' in link_element else "N/A"

            scraped_data.append({
                'name': name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url,
            })
            self.stdout.write(self.style.SUCCESS(f"Scraped: {name} - {price}"))

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Successfully saved scraped data to {output_file}"))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Error writing to file {output_file}: {e}"))
