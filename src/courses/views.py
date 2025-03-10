from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import DesiredClassesForm
import csv
import os
from .models import DesiredCourse
from dataclasses import asdict
from scraper.scrape import get_all_sections
from .misc import get_unique_courses, is_conflicting, get_start_and_end
from apes import settings
from .schedule import Course, generate_timetable

from itertools import product
import numpy as np

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
            # Obtain DCP from `request.session`
            dcp_codes = [
                x['course_code'] for x in request.session.get("dcp", [])
            ]
            print(dcp_codes)

        # Check if course is already in DCP
        if course_code in dcp_codes:
            messages.error(request, "Class already exists.")
        else:
            # Obtain sections of classes in DCP
            dcp_sections = request.session.get("dcp_sections", [])
            
            if dcp_sections == []: # Not cached yet
                dcp_sections = [get_all_sections(code, strict=True) for code in dcp_codes]
                request.session['dcp_sections'] = dcp_sections
                request.session.save()

            # Obtain sections of course to be added
            course_sections = list(filter(
                lambda x: x['course_code'] == course_code,
                request.session['course_sections']
            ))

            timeout = False

            for section in course_sections:
                """Checks if `section`'s timeslots collides with `x`"""
                def is_not_within_range(x) -> bool:
                    course_days = set(list(''.join(list(section['timeslot'].keys()))))
                    x_days = set(list(''.join(list(x['timeslot'].keys()))))

                    for day in list(course_days.intersection(x_days)):
                        print(day)
                        course_start, course_end = get_start_and_end(section['timeslot'], day)
                        x_start, x_end = get_start_and_end(x['timeslot'], day)

                        if not (x_end <= course_start or x_start >= course_end):
                            return False

                    return True

                print("before filtering: ", sum([len(x) for x in dcp_sections]))

                temp = []

                # Pre-filter the DCP sections
                for i, section_lst in enumerate(dcp_sections):
                    temp.append(
                        list(filter(
                            is_not_within_range,
                            section_lst
                        ))
                    )

                print("after filtering: ", ([len(x) for x in temp]))

                for i, dcp_section in enumerate(list(product(*temp))):

                    if not is_conflicting([section] + list(dcp_section)):
                        print([section] + list(dcp_section))
                        if request.user.id:
                            DesiredCourse.objects.create(
                                student_id = request.user.id,
                                course_code = course_code
                            )
                        else:
                            request.session['dcp'].append(course_sections[0])
                            request.session.save()

                        # Append current course's sections to DCP sections
                        request.session['dcp_sections'].append(course_sections)
                        request.session.save()
                        print(f"Sessions's `dcp_sections` now has {len(request.session['dcp_sections'])} sections.")

                        messages.success(request, "Class has been successfully added.")
                        return redirect(reverse('homepage_view'))
                    
                    if i == 100000:
                        timeout = True
                        break
                    
            if timeout:
                messages.error(request, "Couldn't complete request in time.")
            else:
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

def view_sched_view(request, sched_id:int):
    #############################
    # For testing purposes only #
    #############################

    classes = [
        # Course(
        #     course_code="CS 180",
        #     section_name={"lec":"THR"},
        #     capacity=30,
        #     demand=30,
        #     units=3.0,
        #     class_days={"lec":"TH"},
        #     location={"lec":"AECH"},
        #     coords={"lec":(0,0)},
        #     instructor_name={"lec":"ROSELYN GABUD"},
        #     timeslots={"lec":(90,180)},
        #     offering_unit="DCS"
        # ),

        Course(
            course_code="CS 145",
            section_name={"lec":"HONOR", "lab":"HONOR 2"},
            capacity=30,
            demand=1,
            units=4.0,
            class_days={"lec":"TH","lab":"M"},
            location={"lec":"Accenture","lab":"TL2"},
            coords={"lec":(0,0), "lab":(0,0)},
            instructor_name={"lec":"WILSON TAN", "lab":"GINO SAMPEDRO"},
            timeslots={"lec":(450,540), "lab":(240,420)},
            offering_unit="DCS"
        ),

        Course(
            course_code="CS 192",
            section_name={"lec":"TDE2", "lab":"HUV2"},
            capacity=30,
            demand=1,
            units=3.0,
            class_days={"lec":"T", "lab":"H"},
            location={"lec":"AECH", "lab":"AECH"},
            coords={"lec":(0,0), "lab":(0,0)},
            instructor_name={"lec":"ROWENA SOLAMO", "lab":"ROWENA SOLAMO"},
            timeslots={"lec":(180,300), "lab":(180,360)},
            offering_unit="DCS"
        ),

        Course(
            course_code="LIS 51",
            section_name={"lec":"WFU"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"WF"},
            location={"lec":"SOLAIR"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"DRIDGE REYES"},
            timeslots={"lec":(180,270)},
            offering_unit="SLIS"
        ),

        Course(
            course_code="CS 153",
            section_name={"lec":"THW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"TH"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"PHILIP ZUNIGA"},
            timeslots={"lec":(360,450)},
            offering_unit="DCS"
        ),

        Course(
            course_code="CS 132",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"WF"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"PAUL REGONIA"},
            timeslots={"lec":(360,450)},
            offering_unit="DCS"
        ),

        Course(
            course_code="Riana",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"WF"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"THEODORE ESGUERRA"},
            timeslots={"lec":(780,840)},
            offering_unit="DCS"
        ),

        Course(
            course_code="Jopeth",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"WF"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"THEODORE ESGUERRA"},
            timeslots={"lec":(720,780)},
            offering_unit="DCS"
        ),

        Course(
            course_code="G",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"TH"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"THEODORE ESGUERRA"},
            timeslots={"lec":(720,780)},
            offering_unit="DCS"
        ),

        Course(
            course_code="Jason",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"TH"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"THEODORE ESGUERRA"},
            timeslots={"lec":(780,840)},
            offering_unit="DCS"
        ),

        Course(
            course_code="THEO...",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":"S"},
            location={"lec":"AECH"},
            coords={"lec":(0,0)},
            instructor_name={"lec":"THEODORE ESGUERRA"},
            timeslots={"lec":(720,840)},
            offering_unit="DCS"
        ),
    ]

    main_table, export_table = generate_timetable(classes)



    context = {
        "sched_id" : sched_id,
        "main_table" : main_table,
        "export_table" : export_table,
        "courses" : classes,
        "units" : f"{sum([course.units for course in classes])} units",
    }

    return render(request, "view_sched.html", context)

