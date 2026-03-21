from django.core.management.base import BaseCommand
from apps.news.services import fetch_gnews
from apps.news.models import NewsArticle
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Fetch news from GNews"

    def handle(self, *args, **kwargs):

        # 🔥 limpar notícias antigas (1 ano baseado no banco)
        cutoff_date = timezone.now() - timedelta(days=365)

        deleted, _ = NewsArticle.objects.filter(
            created_at__lt=cutoff_date
        ).delete()

        print(f"🧹 Removidas {deleted} notícias antigas")

        # 🔥 buscar novas notícias
        fetch_gnews()

        self.stdout.write("News updated")