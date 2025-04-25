from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserAuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from apes.utils import redirect_authenticated_users

""" Displays the Sign Up page """


@redirect_authenticated_users
def register_view(request):
    # form = UserCreationForm()
    # print("logged in", request.session['username'])
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect(reverse("successful_account_creation"))
    else:
        form = UserRegisterForm()

    context = {
        "form": form,
    }
    return render(request, "register.html", context)


""" Displays message for successful account creation """


@redirect_authenticated_users  # not necessary since fixed already in function; added for consistency purposes
def successful_account_creation_view(request):
    if not messages.get_messages(request):
        return redirect(reverse("register_view"))

    return render(request, "success_create.html", {})


""" Displays the Log In page """


@redirect_authenticated_users
def login_view(request):
    form = UserAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            request.session.flush()

            login(request, user)
            # DEBUGGER: print(request.session.keys())
            request.session.pop(
                "is_guest", None
            )  # when a user logs in, pop the is_guest since no longer a guest

            # DEBUGGER: print(request.session.pop('is_guest', None))
            # DEBUGGER: print(request.session.keys())

            request.session["username"] = request.user.username

            next_url = request.GET.get("next") or reverse("homepage_view")

            # print(next_url)

            return redirect(next_url)

    for error in form.non_field_errors():
        messages.error(request, error)

    context = {
        "form": form,
    }

    return render(request, "login.html", context)
