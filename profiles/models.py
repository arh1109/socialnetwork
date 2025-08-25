from django.db import models

# profiles/models.py
class AboutUser(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='about')
    workplace = models.CharField(max_length=120, blank=True)
    high_school = models.CharField(max_length=120, blank=True)
    college = models.CharField(max_length=120, blank=True)
    current_city = models.CharField(max_length=120, blank=True)
    hometown = models.CharField(max_length=120, blank=True)
    relationship_status = models.CharField(max_length=60, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=40, blank=True)
    pronouns = models.CharField(max_length=40, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    about_you = models.TextField(blank=True)
    name_pronunciation = models.CharField(max_length=120, blank=True)  # one‑and‑only
    nickname = models.CharField(max_length=80, blank=True)             # single value

class Website(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='websites')
    url = models.URLField()

class SocialLink(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='social_links')
    label = models.CharField(max_length=40)  # e.g., Twitter, GitHub
    url = models.URLField()

class Workspace(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)

class LabeledCity(models.Model):
    """For 'add city' history (previous cities, travel, etc.)."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='cities')
    label = models.CharField(max_length=40)  # e.g., 'previous', 'favorite'
    city_name = models.CharField(max_length=120)

class Language(models.Model):
    name = models.CharField(max_length=80, unique=True)

class UserLanguage(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='languages')
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    proficiency = models.CharField(max_length=40, blank=True)
    class Meta:
        unique_together = [('user','language')]
