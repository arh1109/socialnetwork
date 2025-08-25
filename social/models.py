from django.db import models

# social/models.py
class FriendRequest(models.Model):
    from_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sent_requests')
    to_user   = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='received_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='pending')  # pending/accepted/declined
    class Meta:
        unique_together = [('from_user','to_user')]

class Friendship(models.Model):
    """Undirected edge; store one row with a < b invariant to avoid duplicates."""
    user_a = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='friends_a')
    user_b = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='friends_b')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = [('user_a','user_b')]

class FamilyRelation(models.Model):
    profile1 = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='family_out')
    profile2 = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='family_in')
    relation = models.CharField(max_length=40)  # e.g., parent, sibling
    class Meta:
        indexes = [models.Index(fields=['profile1']), models.Index(fields=['profile2'])]
