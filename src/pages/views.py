from django.shortcuts import render

# Create your views here.

def landing_view(request, *args, **kwargs):
    return render(request, "landing.html", {})


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