from django.shortcuts import render, redirect
from django.contrib.auth.forms import BaseUserCreationForm
from .forms import UserRegisterForm, UserAuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse

""" Displays the Sign Up page """
def register_view(request):
    # form = UserCreationForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("successful_account_creation"))
    else:
        form = UserRegisterForm()

    context = {
        'form' : form,
    }
    return render(request, "register.html", context)

""" Displays message for successful account creation """
def successful_account_creation_view(request):
    return render(request, "success_create.html", {})

""" Displays the Log In page """
def login_view(request):
    form = UserAuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(reverse("homepage_view"))

    for error in form.non_field_errors():
        messages.error(request, error)

    return render(request, "login.html", {"form": form})