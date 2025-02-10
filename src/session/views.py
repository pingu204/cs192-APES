from django.shortcuts import render, redirect
from django.contrib.auth.forms import BaseUserCreationForm
from .forms import UserRegisterForm, UserAuthenticationForm
from django.contrib.auth import login
from django.contrib import messages

""" Displays the Sign Up page """
def register_view(request):
    # form = UserCreationForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success/')
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
    if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("../home/") # FIX: redirect; placeholder = #
        
            # change redirect of register_view() as well // OPTIONAL
            # in the meantime, set "/homepage" or "/home" as target?
            
              
        else:
            # error accumulator
            for error in form.errors.get("__all__", []):  
                messages.error(request, error)
    
    else:
        form = UserAuthenticationForm()

    context = {
        'form' : form,
    }

    return render(request, "login.html", context)