from django.shortcuts import render
from .forms import DesiredClassesForm


# Create your views here.

def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm()

    if request.GET.get("course_code"):
        # get the raw query search placed by the user
        raw_search_query = request.GET["course_code"]
        # clean the raw search query such that spaces are resolved;
        cleaned_search_query = (' '.join(raw_search_query.split())).upper()

 
        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print(f"User's cleaned query: {cleaned_search_query}")

        # Primary Logic (?): if cleaned_search_query == row['course_code'] then append to search_results

        # pwede rin check muna if wala, i.e., cleaned_search_query in [course_code1, course_code2, ...]

        # Now, we use this cleaned_search_query to match a course code! only EXACT MATCHING COURSE CODES
        # i.e. .startswith("course_code") can be used?
        ...
    else: # Normal Loading

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print("Enter DEFAULT /add/ routing")
        ...

    context = {
        "form" : form,
        "search_results" : search_results,
    }

    return render(request, "dcp_add.html", context)