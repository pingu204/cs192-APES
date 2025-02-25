from django.shortcuts import render
from .forms import DesiredClassesForm
from django.contrib import messages
import pandas as pd
import os

# Create your views here.

def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm(request.GET)
    # from copilot:
    # Get the current working directory (CWD)
    cwd = os.path.dirname(__file__)
    # Navigate up one directory level
    relative_path = os.path.join(cwd, '..', 'scraper', 'csv', 'courses.csv')
    # Resolve the relative path to an absolute path
    absolute_path = os.path.abspath(relative_path)
    courses = pd.read_csv(absolute_path)
    # print(courses)
    courselist = (courses["course_code"].tolist())
    # print(courselist)

    if request.GET.get("course_code"):
        # get the raw query search placed by the user
        if form.is_valid():
            print("well yes!")
        else:
            print("help")
        """ raw_search_query = request.GET["course_code"]
        print("got: " + raw_search_query)
        # clean the raw search query such that spaces are resolved;
        cleaned_search_query = (' '.join(raw_search_query.split())).upper()

 
        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print(f"User's cleaned query: {cleaned_search_query}")

        # Primary Logic (?): if cleaned_search_query == row['course_code'] then append to search_results

        # pwede rin check muna if wala, i.e., cleaned_search_query in [course_code1, course_code2, ...]
        if cleaned_search_query.upper() not in courselist and cleaned_search_query.capitalize() not in courselist: # UC3-S4 
            # print("class does not exist")
            messages.error(request, "Class does not exist. Try checking if the entered class code is correct.") """
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