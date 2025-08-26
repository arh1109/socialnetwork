# feed/urls.py
from django.urls import path
from .views import home_view, create_post, add_comment

urlpatterns = [
    path("", home_view, name="home"),
    path("post/create/", create_post, name="post_create"),
    path("post/<int:post_id>/comment/", add_comment, name="add_comment"),
]
