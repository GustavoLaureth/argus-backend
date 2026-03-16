from django.db import models
from django.contrib.auth.models import User

class Generation(models.Model):

    CONTENT_TYPES = [
        ("news", "News"),
        ("social", "Social"),
        ("headline", "Headline"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    input_text = models.TextField()

    output_text = models.TextField()

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)