from django.db import models
from django.utils import timezone

# feed/models.py
class Post(models.Model):
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='posts')
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True) 

class Media(models.Model):
    POST = 'post'
    PHOTO = 'photo'
    VIDEO = 'video'
    kind = models.CharField(max_length=10, choices=[(PHOTO,'photo'),(VIDEO,'video')], default=PHOTO)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='media/')  # S3
    thumbnail = models.ImageField(upload_to='thumbs/', blank=True, null=True)  # pre-generate for videos

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = [('post','user')]

class PhotoTag(models.Model):
    """Rectangular tag drawn over an image; store normalized [0,1] coords."""
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='tags')
    tagged_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='photo_tags')
    x = models.FloatField(); y = models.FloatField(); w = models.FloatField(); h = models.FloatField()
