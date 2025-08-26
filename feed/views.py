# feed/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.http import HttpResponseForbidden

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

    form = PostCreateForm(request.POST, request.FILES)
    if not form.is_valid():
        # Re-render page with errors (no redirect)
        posts = (Post.objects
                 .filter(author=request.user)
                 .select_related('author')
                 .prefetch_related('media', 'comments')
                 .order_by('-created_at')[:25])
        return render(request, "feed/home.html", {"form": form, "posts": posts})

    post = Post.objects.create(author=request.user, text=form.cleaned_data['text'])
    for f in request.FILES.getlist("attachments"):
        ctype = f.content_type or ""
        kind = Media.PHOTO if ctype.startswith("image/") else Media.VIDEO if ctype.startswith("video/") else None
        if kind:
            Media.objects.create(post=post, kind=kind, file=f)

    messages.success(request, "Posted!")
    return redirect(reverse("home") + "#composer")  # scrolls to the composer

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = (request.POST.get("comment_text") or "").strip()
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
    return redirect("home")
