from django.shortcuts import render, redirect
from django.contrib.auth.forms import BaseUserCreationForm
from .forms import UserRegisterForm
# Create your views here.
def register_view(request):
    # form = UserCreationForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('apes:/')
    else:
        form = UserRegisterForm()

    context = {
        'form' : form,
    }
    return render(request, "register.html", context)