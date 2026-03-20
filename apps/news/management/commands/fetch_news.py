from django.core.management.base import BaseCommand
from apps.news.services import fetch_gnews
from apps.news.models import NewsArticle
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Fetch news from GNews"

    def handle(self, *args, **kwargs):
        # 🔥 1. limpar notícias antigas (6 meses)
        cutoff_date = timezone.now() - timedelta(days=365)

        deleted, _ = NewsArticle.objects.filter(
            published_at__lt=cutoff_date
        ).delete()

        print(f"🧹 Removidas {deleted} notícias antigas")

        # 🔥 2. buscar novas notícias (seu código atual)
        fetch_gnews()
        self.stdout.write("News updated")