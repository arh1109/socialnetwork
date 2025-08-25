from django.db import models

# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # username is unique by default; keep email null/optional for now
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    cover_photo = models.ImageField(upload_to="covers/", blank=True, null=True)

class UserBasicInfo(models.Model):
    """Denormalized lightweight card; cacheable for fast friend lists."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basic")
    display_name = models.CharField(max_length=80)
    num_friends = models.PositiveIntegerField(default=0)  # keep in sync via signals
