from django.shortcuts import render, redirect
from django.contrib.auth.forms import BaseUserCreationForm
from .forms import UserRegisterForm, UserAuthenticationForm
from django.contrib.auth import authenticate, login, logout
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

    """if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            print(form.get_user())
            login(request, form.get_user())
            return redirect("../home/") # FIX: redirect; placeholder = #
        
            # change redirect of register_view() as well // OPTIONAL
            # in the meantime, set "/homepage" or "/home" as target?
            
              
        else:
            print("naw")
            # error accumulator
            for error in form.errors.get("__all__", []):  
                messages.error(request, error)
    
    else:
        form = UserAuthenticationForm()
    """

    """    
    if request.method == "POST":
        username = request.POST['username'] #name='username'
        password = request.POST['password'] #name='password  (in login.html)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse("homepage_view"))
        else:
            messages.success(request, ("There was an error logging in. Please try again."))
            return redirect(reverse("login_view"))
    
    else:
        context = {}
        return render(request, "login.html", context)"""
    
    if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse("homepage_view"))
    else:
        form = UserAuthenticationForm()

    context = {
        'form' : form
    }

    return render(request, 'login.html', context)