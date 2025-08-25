# accounts/views.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .forms import RegisterForm

User = get_user_model()

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            messages.success(request, "Account created. You’re now logged in.")
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

