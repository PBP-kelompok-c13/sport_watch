import requests
from bs4 import BeautifulSoup
import json
from django.core.management.base import BaseCommand
import datetime
from urllib.parse import urljoin

class Command(BaseCommand):
    help = 'Scrapes news from kompas.com/sports and saves it to a JSON file.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting scraping from kompas.com/sports...'))
        
        url = 'https://www.kompas.com/sports'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Error fetching URL {url}: {e}"))
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_data = []
        articles = soup.find_all('article', class_='list-content__item') # Placeholder, needs adjustment for Kompas
        scraped_count = 0
        MAX_ARTICLES = 50

        for article in articles:
            if scraped_count >= MAX_ARTICLES:
                break

            title_tag = article.find('h2') # Placeholder, needs adjustment for Kompas
            link_tag = article.find('a')
            image_tag = article.find('img')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''

                try:
                    # Fetch the detail page for content
                    detail_response = requests.get(link)
                    detail_response.raise_for_status()
                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                    
                    # Extract title from the detail page for accuracy
                    detail_title_tag = detail_soup.find('h1') # Assuming h1 is the main title on the detail page
                    if detail_title_tag:
                        title = detail_title_tag.get_text(strip=True)
                    else:
                        self.stdout.write(self.style.WARNING(f"Could not find main title on detail page for {link}. Using title from main page."))
                        # Keep the title from the main page if detail title not found

                    # Extract content (adjust selector as needed)
                    content_div = detail_soup.find('div', class_='detail__body-text') # Placeholder, needs adjustment for Kompas
                    content = content_div.get_text(strip=True) if content_div else 'No content found.'

                    news_data.append({
                        'title': title,
                        'content': content,
                        'category': 'Olahraga',
                        'image_url': image_url,
                        'source_url': link,
                        'published_date': str(datetime.datetime.now()) # Using datetime.datetime.now() for consistency, though not strictly needed for JSON
                    })
                    self.stdout.write(self.style.SUCCESS(f'Successfully scraped: {title}'))
                    scraped_count += 1
                except requests.exceptions.RequestException as e:
                    self.stderr.write(self.style.ERROR(f"Error fetching detail URL {link}: {e}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error processing article {title}: {e}"))

        # Write data to JSON file
        file_path = 'kompas_sports_news.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Scraping finished. Data saved to {file_path}'))
