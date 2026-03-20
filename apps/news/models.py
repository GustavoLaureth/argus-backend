from django.db import models

class NewsArticle(models.Model):

    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    source = models.CharField(max_length=255)
    url = models.URLField()

    published_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title