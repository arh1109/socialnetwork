from django.db import models

# notifications/models.py
class Notification(models.Model):
    """Simple fan-out; render in a dropdown."""
    to_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=30)  # friend_request, friend_accept, like, comment, tag
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey('feed.Post', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # Create notifications via signals on FriendRequest/Like/Comment/PhotoTag
