from django.urls import path
from .views import profile_detail

urlpatterns = [
    path("<str:username>/", profile_detail, name="profile"),
]
