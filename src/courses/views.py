from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import DesiredClassesForm
import csv
import os
from .models import Course, DesiredCourse
from dataclasses import asdict
from scraper.scrape import get_all_sections
from .misc import get_unique_courses, is_conflicting_with_dcp
from apes import settings

from itertools import product

from django.contrib import messages

def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm(request.GET)

    if request.method == "POST":
        # Handle the POST request to save the class code
        print(request.POST.get("course_code"))

        course_code = request.POST.get("course_code")
        
        if request.user.id:
            # Obtain DCP from database
            dcp_codes = [
                x.course_code for x in list(DesiredCourse.objects.filter(student_id = request.user.id))
            ]
        else: # Guest user
            # Obtain DCP from `request.session``
            dcp_codes = [
                x['course_code'] for x in request.session.get("dcp", [])
            ]
            print(dcp_codes)

        # Check if course is already in DCP
        if course_code in dcp_codes:
            messages.error(request, "Class already exists.")
        else:
            # Scrape sections of classes in DCP
            dcp_sections = [get_all_sections(code, strict=True) for code in dcp_codes]

            # Obtain sections of course to be added
            course_sections = list(filter(
                lambda x: x['course_code'] == course_code,
                request.session['course_sections']
            ))

            # Loop through each combination to see if there's a viable
            # -- Only need to look for ONE possible schedule
            for section in course_sections:
                for dcp_section in list(product(*dcp_sections)):

                    # Check if the course to be added conflicts with the classes currently in DCP
                    if not is_conflicting_with_dcp(section, list(dcp_section)):
                        
                        if request.user.id:
                            DesiredCourse.objects.create(
                                student_id = request.user.id,
                                course_code = course_code
                            )
                        else: # Guest user
                            request.session['dcp'].append(course_sections[0])   # Dummy course!
                                                                                # -- other fields don't matter
                            
                            # Necessary for `request.session` to be used in another view
                            request.session.save()
                            
                            # DEBUGGING
                            # print(request.session['dcp'])

                        messages.success(request, "Class has been successfully added.")
                        return redirect(reverse('homepage_view'))
            
            messages.error(request, "Class conflicts with another class.")
    
    elif request.GET.get("course_code"):
        form = DesiredClassesForm(request.GET)

        # Obtain the raw query text inputted by the user
        raw_search_query = request.GET["course_code"]

        # Clean the `raw_search_query` such that whitespaces are omitted
        cleaned_search_query = (' '.join(raw_search_query.split())).upper()

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print(f"User's cleaned query: {cleaned_search_query}")
        
        csv_file_path = os.path.join(settings.BASE_DIR, "scraper", "csv", "courses.csv")

        if form.is_valid():

            # Obtain all sections associated with `raw_search_query` course code
            course_sections = get_all_sections(cleaned_search_query)

            request.session['course_sections'] = course_sections
            search_results = get_unique_courses(course_sections)
    
    else: # Normal Loading

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print("Enter DEFAULT /add/ routing")
        ...

    context = {
        "form" : form,
        "search_results" : search_results,
    }

    return render(request, "dcp_add.html", context)
