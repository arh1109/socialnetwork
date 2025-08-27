from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from feed.models import Post, Media
from feed.forms import PostCreateForm  # reuse composer form, already built

User = get_user_model()

def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user.is_authenticated and request.user.id == profile_user.id

    # Optional fields (bio / relationship_status) – use whatever you have
    bio = getattr(profile_user, "bio", None)
    relationship_status = getattr(profile_user, "relationship_status", None)

    # Recent photos (3x3 grid)
    qs = Media.objects.filter(kind="photo", post__author=profile_user)
    # order by created_at if present, else id
    if "created_at" in [f.name for f in Media._meta.get_fields()]:
        qs = qs.order_by("-created_at")
    else:
        qs = qs.order_by("-id")
    recent_photos = list(qs[:9])
    photo_placeholders = range(max(0, 9 - len(recent_photos)))

    # Friends preview (3x3). Adjust if your relation differs; else empty.
    friends_qs = []
    if hasattr(profile_user, "friends"):
        try:
            friends_qs = list(profile_user.friends.all()[:9])
        except Exception:
            friends_qs = []
    friends_preview = friends_qs
    friend_placeholders = range(max(0, 9 - len(friends_preview)))
    friend_count = len(friends_qs) if friends_qs else 0
    try:
        # if .friends.count() works, prefer it
        friend_count = profile_user.friends.count()
    except Exception:
        pass

    # User wall – for now: posts authored by this user
    posts = (Post.objects
             .filter(author=profile_user)
             .select_related("author")
             .prefetch_related("media", "comments")
             .order_by("-created_at"))

    ctx = {
        "profile_user": profile_user,
        "is_owner": is_owner,
        "bio": bio,
        "relationship_status": relationship_status,
        "recent_photos": recent_photos,
        "photo_placeholders": photo_placeholders,
        "friends_preview": friends_preview,
        "friend_placeholders": friend_placeholders,
        "friend_count": friend_count,
        "posts": posts,
        "form": PostCreateForm(),  # composer
    }
    return render(request, "profiles/profile.html", ctx)

