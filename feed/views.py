# feed/views.py
from django.shortcuts import render

def home_view(request):
    """
    Splash page for logged-out users; lightweight home for logged-in users.
    """
    return render(request, "feed/home.html")