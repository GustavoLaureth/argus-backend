from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class UserProfile(models.Model):

    PLAN_CHOICES = [
        ("free", "Free"),
        ("starter", "Starter"),
        ("creator", "Creator"),
        ("pro", "Pro"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="free"
    )

    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    stripe_subscription_id = models.CharField(
    max_length=255,
    blank=True,
    null=True
)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        UserProfile.objects.create(user=instance)