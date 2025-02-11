from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
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


def logout_view(request, *args, **kwargs):
    # if POST method, ensures that users don't logout by simply rerouting to /logout/
    if request.method == 'POST':
        logout(request)
        # messages.success(request, ("Successfully Logged Out.")) # optional (if we want to display an error message to the users, then just add here)
        return redirect(reverse("landing_view"))
    
    if request.user.is_authenticated:
        return redirect(reverse("homepage_view"))
    else:
        return redirect(reverse("landing_view"))