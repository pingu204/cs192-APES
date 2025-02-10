from django.shortcuts import render

# Create your views here.

def landing_view(request, *args, **kwargs):
    return render(request, "landing.html", {})


def homepage_view(request, *args, **kwargs):
    context = {}
    return render(request, "homepage.html", context)