# feed/services.py
from django.db import models
from social.models import Friendship
from .models import Post

def feed_for(user):
    """Return a queryset of posts authored by the user's friends."""
    friend_pairs = (Friendship.objects
                    .filter(models.Q(user_a=user) | models.Q(user_b=user))
                    .values_list('user_a', 'user_b'))

    # Flatten friend IDs, drop self
    friend_ids = {uid for pair in friend_pairs for uid in pair if uid != user.id}

    return (Post.objects
            .filter(author_id__in=friend_ids)
            .select_related('author')
            .prefetch_related('media', 'comments', 'likes')
            .order_by('-created_at'))