# feed/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


from .forms import PostCreateForm
from .models import Post, Media, Comment
from social.models import Friendship
from django.urls import reverse

def _friend_ids(user):
    # friends set (works even if you haven’t wired Friendship yet)
    pairs = (Friendship.objects
             .filter(models.Q(user_a=user) | models.Q(user_b=user))
             .values_list('user_a', 'user_b'))
    ids = {uid for a, b in pairs for uid in (a, b) if uid != user.id}
    # always include your own id so you see your posts
    ids.add(user.id)
    return ids

def home_view(request):
    # Composer form (only for logged-in users)
    form = PostCreateForm() if request.user.is_authenticated else None

    posts_qs = Post.objects.all().order_by('-created_at')
    if request.user.is_authenticated:
        ids = _friend_ids(request.user)
        posts_qs = posts_qs.filter(author_id__in=ids)
    posts_qs = posts_qs.select_related('author').prefetch_related('media', 'comments', 'comments__author')

    return render(request, "feed/home.html", {
        "form": form,
        "posts": posts_qs[:25],  # basic pagination later
    })

@login_required
def create_post(request):
    if request.method != "POST":
        return HttpResponseForbidden()

    form = PostCreateForm(request.POST)
    files = request.FILES.getlist("attachments")
    print("DEBUG create_post: got files ->", [f.name for f in files])
    text = (request.POST.get("text") or "").strip()

    # Require text OR at least 1 file
    if not text and not files:
        messages.error(request, "Write something or add at least one photo/video.")
        posts = (Post.objects
                 .filter(author=request.user)
                 .select_related('author')
                 .prefetch_related('media', 'comments')
                 .order_by('-created_at')[:25])
        return render(request, "feed/home.html", {"form": form, "posts": posts})

    if not form.is_valid():  # validates just the text field
        posts = (Post.objects
                 .filter(author=request.user)
                 .select_related('author')
                 .prefetch_related('media', 'comments')
                 .order_by('-created_at')[:25])
        return render(request, "feed/home.html", {"form": form, "posts": posts})

    # Create the post
    post = Post.objects.create(author=request.user, text=form.cleaned_data.get("text", ""))

    # Attach media
    for f in files:
        ctype = (f.content_type or "").lower()
        if ctype.startswith("image/"):
            kind = Media.PHOTO
        elif ctype.startswith("video/"):
            kind = Media.VIDEO
        else:
            continue
        Media.objects.create(post=post, kind=kind, file=f)

    messages.success(request, "Posted!")
    return redirect(reverse("home") + "#composer")

@login_required
@require_POST
def edit_post(request, pk):
    from .models import Post  # local import to keep snippet compact
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Not found"}, status=404)

    if post.author_id != request.user.id:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    new_text = (request.POST.get("text") or "").strip()
    post.text = new_text
    post.edited_at = timezone.now()
    post.save(update_fields=["text", "edited_at"])
    return JsonResponse({
        "ok": True,
        "text": new_text,
        "edited": True,
        "edited_at": post.edited_at.isoformat(),
    })

@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author_id != request.user.id:
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    # 1) delete media rows (signals remove files)
    medias = list(post.media.all())
    for m in medias:
        m.delete()  # triggers post_delete -> files removed

    # 2) delete the post (comments should cascade if FK has on_delete=CASCADE)
    post.delete()

    return JsonResponse({"ok": True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = (request.POST.get("comment_text") or "").strip()
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
    return redirect("home")
