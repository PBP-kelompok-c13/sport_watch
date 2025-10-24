import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Scrapes product data from footlocker.id/men.html and saves it to a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, help='Path to the output JSON file', default='footlocker_men.json')

    def handle(self, *args, **options):
        output_file = options['output']
        self.scrape_footlocker_men(output_file)

    def scrape_footlocker_men(self, output_file):
        URL = "https://www.footlocker.id/men.html"
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
            link_element = product.find("a", class_="product-item-photo")
            
            # Find the image element more robustly
            image_element = product.find("img") # Find any img tag within the product item
            if not image_element:
                image_element = product.find("source", srcset=True) # Sometimes images are in <source> tags

            # Find brand by looking for a div with specific class or by its position
            brand_element = product.find("div", class_="product-item-brand") # This was the original attempt
            if not brand_element:
                # If the above fails, try to find the brand as the text content of a div that is a direct child of product
                # This is a more generic approach and might need refinement
                brand_divs = product.find_all("div")
                if len(brand_divs) > 1: # Assuming the brand is in one of the first few divs
                    brand = brand_divs[1].get_text(strip=True) # This is a guess, might need adjustment
                else:
                    brand = "N/A"
            else:
                brand = brand_element.get_text(strip=True)

            name = name_element.get_text(strip=True) if name_element else "N/A"
            price_str = price_element.get_text(strip=True) if price_element else "Rp. 0"
            price = float(price_str.replace("Rp.", "").replace(".", "").strip()) if price_str != "N/A" else 0.0
            
            image_url = "N/A"
            if image_element:
                image_url = image_element.get('src') or image_element.get('data-src') or image_element.get('srcset')
                if not image_url: # Fallback if neither src nor data-src nor srcset is found
                    image_url = "N/A"

            product_url = link_element['href'] if link_element and 'href' in link_element.attrs else "N/A"
            
            category = "Men's Shoes"

            scraped_data.append({
                'name': name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url,
                'brand': brand,
                'category': category,
                'description': f"Product URL: {product_url}",
            })
            self.stdout.write(self.style.SUCCESS(f"Scraped: {name} - {price} - {brand} - {image_url} - {product_url}"))

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Successfully saved scraped data to {output_file}"))
        except IOError as e:
            self.stdout.write(self.style.ERROR(f"Error writing to file {output_file}: {e}"))
