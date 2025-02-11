from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from apes.utils import redirect_authenticated_users

# Create your views here.

@redirect_authenticated_users
def landing_view(request, *args, **kwargs):
    return render(request, "landing.html", {})

@login_required
def homepage_view(request, *args, **kwargs):
    context = {
        "user" : request.user
    }
    return render(request, "homepage.html", context)


# insert decorator delimiter (access permissions?)
def guest_view(request, *args, **kwargs):
    context = {
        "user" : None
    }

    return render(request, "homepage.html", context)