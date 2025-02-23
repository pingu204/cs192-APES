from django.shortcuts import render
from .forms import DesiredClassesForm

# Create your views here.
def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm()

    if request.GET.get("course"):
        ...
    else: # Normal Loading
        ...

    context = {
        "form" : form,
        "search_results" : search_results,
    }

    return render(request, "dcp_add.html", context)