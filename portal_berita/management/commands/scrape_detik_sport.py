import requests
from bs4 import BeautifulSoup
import json
from django.core.management.base import BaseCommand
import datetime
from urllib.parse import urljoin

class Command(BaseCommand):
    help = 'Scrapes news from sport.detik.com and saves it to a JSON file.'

    MAX_ARTICLES = 100 # Target number of articles to scrape

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting scraping from sport.detik.com...'))

        base_url = 'https://sport.detik.com/'
        current_url = base_url
        news_data = []
        scraped_count = 0

        # Find the 'Indeks' link on the main page
        indeks_link = None
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for a link with 'Indeks' in its text or href
            indeks_link_tag = soup.find('a', string=lambda text: text and 'Indeks' in text)
            if indeks_link_tag and 'href' in indeks_link_tag.attrs:
                indeks_link = indeks_link_tag['href']
                self.stdout.write(self.style.SUCCESS(f"Found Indeks link: {indeks_link}"))
            else:
                self.stdout.write(self.style.WARNING("Could not find 'Indeks' link on the main page. Scraping only from the main page."))
        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Error fetching main URL {base_url}: {e}"))
            return

        if indeks_link:
            current_url = indeks_link

        while scraped_count < self.MAX_ARTICLES and current_url:
            try:
                response = requests.get(current_url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.stderr.write(self.style.ERROR(f"Error fetching URL {current_url}: {e}"))
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all('article', class_='list-content__item')

            for article in articles:
                if scraped_count >= self.MAX_ARTICLES:
                    break

                title_tag = article.find('h2')
                link_tag = article.find('a')
                image_tag = article.find('img')

                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''

                    try:
                        detail_response = requests.get(link)
                        detail_response.raise_for_status()
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                        # Extract title from the detail page for accuracy
                        detail_title_tag = detail_soup.find('h1') # Assuming h1 is the main title on the detail page
                        if detail_title_tag:
                            title = detail_title_tag.get_text(strip=True)
                        else:
                            self.stdout.write(self.style.WARNING(f"Could not find main title on detail page for {link}. Using title from main page."))

                        content_div = detail_soup.find('div', class_='detail__body-text')
                        content = content_div.get_text(strip=True) if content_div else 'No content found.'

                        news_data.append({
                            'title': title,
                            'content': content,
                            'category': 'Olahraga',
                            'image_url': image_url,
                            'source_url': link,
                            'published_date': str(datetime.datetime.now())
                        })
                        self.stdout.write(self.style.SUCCESS(f'Successfully scraped: {title}'))
                        scraped_count += 1
                    except requests.exceptions.RequestException as e:
                        self.stderr.write(self.style.ERROR(f"Error fetching detail URL {link}: {e}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing article {title}: {e}"))

            # Find the next page link (adjust selector based on Indeks page structure)
            next_page_link = None
            # Try to find a 'Next' button or a link to the next page number
            next_button = soup.find('a', string=lambda text: text and ('Next' in text or '>' == text.strip()))
            if next_button and 'href' in next_button.attrs:
                next_page_link = next_button['href']
            else:
                # If no explicit 'Next' button, try to find numbered pagination
                # This is a generic approach and might need specific adjustment for detik.com's indeks page
                current_page_item = soup.find('a', class_='active') # Assuming active page has a class 'active'
                if current_page_item:
                    current_page_num = int(current_page_item.get_text(strip=True))
                    next_page_num = current_page_num + 1
                    # This assumes a predictable URL structure for next pages
                    # e.g., /indeks/page/2, /indeks/page/3
                    # This is highly speculative and will likely need adjustment
                    # For now, we will just try to find a link with the next page number
                    next_page_num_link = soup.find('a', string=str(next_page_num))
                    if next_page_num_link and 'href' in next_page_num_link.attrs:
                        next_page_link = next_page_num_link['href']

            if next_page_link:
                # Ensure the next_page_link is an absolute URL
                if not next_page_link.startswith('http'):
                    current_url = urljoin(current_url, next_page_link)
                else:
                    current_url = next_page_link
            else:
                self.stdout.write(self.style.WARNING('No more pages found or target articles reached.'))
                current_url = None # Stop the loop

        # Write data to JSON file
        file_path = 'detik_sport_news.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Scraping finished. Data saved to {file_path}'))
