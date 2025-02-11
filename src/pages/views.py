from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

# Create your views here.

def landing_view(request, *args, **kwargs):
    return render(request, "landing.html", {})

@login_required(login_url=reverse_lazy("login_view"))
def homepage_view(request, *args, **kwargs):
    context = {
        "user" : request.user
    }
    return render(request, "homepage.html", context)

def guest_view(request, *args, **kwargs):
    context = {
        "user" : None
    }

    return render(request, "homepage.html", context)