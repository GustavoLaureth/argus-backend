import requests
from django.conf import settings
from .models import NewsArticle
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def fetch_gnews():

    url = "https://gnews.io/api/v4/top-headlines"

    params = {
        "lang": "pt",
        "country": "br",
        "max": 100,
        "apikey": settings.GNEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    for article in data.get("articles", []):

        # evita duplicar
        if not NewsArticle.objects.filter(url=article["url"]).exists():

            NewsArticle.objects.create(
                title=article["title"],
                description=article.get("description"),
                content=article.get("content"),
                source=article["source"]["name"],
                url=article["url"],
                published_at=article["publishedAt"]
            )

    old_news = NewsArticle.objects.filter(
      published_at__lt=timezone.now() - timedelta(days=2)
    )

    deleted_count = old_news.count()
    old_news.delete()

def search_news(query):

    words = query.lower().split()

    articles = NewsArticle.objects.all()

    scored = []

    for article in articles:

        text = (
            (article.title or "") + " " +
            (article.description or "")
        ).lower()

        score = 0

        # 🔥 peso forte no título
        score += sum(word in (article.title or "").lower() for word in words) * 3

        # peso médio na descrição
        score += sum(word in text for word in words)

        # 🔥 bônus por recência
        if article.published_at:
            hours_old = (timezone.now() - article.published_at).total_seconds() / 3600

            if hours_old < 6:
                score += 5
            elif hours_old < 24:
                score += 3
            elif hours_old < 72:
                score += 1

        # só entra se tiver relevância mínima
        if score > 0:
            scored.append((score, article))

    # ordena por score
    scored.sort(reverse=True, key=lambda x: x[0])

    # 🔥 limita (ESSENCIAL)
    return [a for _, a in scored[:10]]

def build_context(articles):

    context = ""

    for i, article in enumerate(articles, 1):

        context += f"""
Fonte {i}:
Título: {article.title}
Data: {article.published_at.strftime('%d/%m/%Y') if article.published_at else 'N/A'}
Resumo: {article.description[:200]}
"""

    return context