from django.shortcuts import render
from .forms import PreferencesForm

# Create your views here.
def modify_preferences_view(request):
    form = PreferencesForm(request.POST, request=request)
    
    context = {
        "form": form,
   
    }

    return render(request, "preferences.html", context)