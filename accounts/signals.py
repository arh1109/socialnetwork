# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from profiles.models import AboutUser
from .models import UserBasicInfo

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_shells(sender, instance, created, **kwargs):
    if created:
        UserBasicInfo.objects.get_or_create(user=instance, defaults={
            "display_name": instance.username
        })
        AboutUser.objects.get_or_create(user=instance)