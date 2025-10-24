import json
from django.core.management.base import BaseCommand
from portal_berita.models import Berita, KategoriBerita
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Loads news data from detik_sport_news.json into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to load news from detik_sport_news.json...'))
        
        file_path = 'detik_sport_news.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: {file_path} not found. Please run 'python manage.py scrape_detik_sport' first."))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Error: Could not decode JSON from {file_path}. Check file format."))
            return

        # Find the category for 'Olahraga' (Sports) or create it if it doesn't exist
        kategori, created = KategoriBerita.objects.get_or_create(nama='Olahraga')
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new category: {kategori.nama}"))

        for item in news_data:
            title = item.get('title')
            content = item.get('content')
            image_url = item.get('image_url', '')
            source_url = item.get('source_url', '')
            published_date_str = item.get('published_date')

            if not title or not content:
                self.stdout.write(self.style.WARNING(f"Skipping news item due to missing title or content: {item}"))
                continue

            # Check if the news already exists to avoid duplicates
            if not Berita.objects.filter(judul=title).exists():
                try:
                    berita = Berita.objects.create(
                        judul=title,
                        konten=content,
                        kategori=kategori,
                        thumbnail=image_url,
                        sumber=source_url,
                        is_published=True
                    )
                    if published_date_str:
                        try:
                            # Parse the date string and make it timezone-aware
                            published_date = datetime.datetime.fromisoformat(published_date_str)
                            berita.tanggal_dibuat = timezone.make_aware(published_date)
                            berita.save()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Could not parse published_date: {published_date_str}. Using current time."))
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully loaded: {title}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error saving news item {title}: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping existing news item: {title}'))

        self.stdout.write(self.style.SUCCESS('Finished loading news.'))
