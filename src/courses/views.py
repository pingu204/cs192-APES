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
    form = DesiredClassesForm()

    if request.method == "POST":
        # Handle the POST request to save the class code
        print(request.POST.get("course_code"))

        course_code = request.POST.get("course_code")
        
        if request.user.id:
            # Obtain DCP from database
            dcp_codes = [
                x.course_code for x in list(DesiredCourse.objects.filter(student_id = request.user.id))
            ]
        else:
            # Guest user -> Obtain DCP from session
            dcp_codes = [
                x['course_code'] for x in request.session.get("dcp", [])
            ]
            print(dcp_codes)

        # Scrape sections of classes in DCP
        dcp_sections = [get_all_sections(code, strict=True) for code in dcp_codes]

        # Get sections of course to be added
        course_sections = list(filter(
            lambda x: x['course_code'] == course_code,
            request.session['course_sections']
        ))

        flag = False
        for section in course_sections:
            for dcp_section in list(product(*dcp_sections)):
                print(dcp_section)
                print(section)
                if not is_conflicting_with_dcp(section, list(dcp_section)):
                    print("goods")
                    if request.user.id:
                        DesiredCourse.objects.create(
                            student_id = request.user.id,
                            course_code = course_code
                        )
                    else:
                        request.session['dcp'].append(course_sections[0])
                        request.session.save()
                        print(request.session['dcp'])
                    messages.success(request, "Class has been successfully added.")
                    return redirect(reverse('homepage_view'))
        
        messages.error(request, "Class conflicts with another class.")
                
        """ course_code = request.POST.get("course_code")
        course_title = request.POST.get("course_title")
        print("ADDED", course_code, "TO DCP")
        # Retrieve the current dcp from the session or initialize it if not present
        dcp = request.session.get('dcp', [])
        # Add the new course code to the dcp
        course_title = course_title.split(' ', 2)  # Split the string into at most 3 parts
        course_title = ' '.join(course_title[:2])
        all_sections = getting_section_details(course_code, course_title)
       
        for _, row in all_sections.iterrows():
            if row['course_code'] == course_code:
                course = Course(
                    course_code=row['course_code'],
                    course_title=row['course_title'],
                    offering_unit=row['offering_unit'],
                    units=float(row['units']),
                    timeslot=row['timeslot'],
                    venue=row['venue'],
                    instructor=row['instructor']
                )
                print("FOUND  COURSE", course)
                # Convert the Course object to a dictionary
                course_dict = asdict(course)
                dcp.append(course_dict)
                
                print("added finally the dcp", row)
                print("THIS IS DCP", dcp)
                    
       
        # Update the session with the new dcp
        request.session['dcp'] = dcp """
        
        # return redirect('homepage_view')
    
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

            # test: temporary DCP
            """ dcp_codes = ['CS 132', 'CS 180']
            dcp_sections = [get_all_sections(code, strict=True) for code in dcp_codes]
 """
            request.session['course_sections'] = course_sections
            search_results = get_unique_courses(course_sections)

        # To-do: Check if conflicting!

        # Now, we use this cleaned_search_query to match a course code! only EXACT MATCHING COURSE CODES
        # i.e. .startswith("course_code") can be used?
    
    else: # Normal Loading

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print("Enter DEFAULT /add/ routing")
        ...

    context = {
        "form" : form,
        "search_results" : search_results,
    }

    return render(request, "dcp_add.html", context)
