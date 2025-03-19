from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import DesiredClassesForm
import csv
import os
from .models import DesiredCourse
from dataclasses import asdict
from scraper.scrape import get_all_sections, couple_lec_and_lab, print_dict
from .misc import get_unique_courses, is_conflicting, get_start_and_end
from apes import settings
from .schedule import Course, generate_timetable
from apes.utils import get_course_details_from_csv

from courses.models import SavedSchedule, SavedCourse

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
            print (dcp_codes)
        else: # Guest user
            # Obtain DCP from `request.session`
            dcp_codes = [
                x['course_code'] for x in request.session.get("dcp", [])
            ]
            print(dcp_codes)
            
        dcp = get_course_details_from_csv(dcp_codes)
        total_units = sum([course['units'] for course in dcp])
        
        print ("TOTAL UNITSSSSS ->>: " ,total_units)
        
        # Check if course is already in DCP
        if course_code in dcp_codes:
            messages.error(request, "Class already exists.")
        elif (total_units +  (get_course_details_from_csv(course_code))[0]['units']) > 30:
            messages.error(request, "Units exceed 30.")
        else:
            # Obtain sections of classes in DCP
            dcp_sections = request.session.get("dcp_sections", [])

            # Obtain sections of course to be added
            course_sections = list(filter(
                lambda x: x['course_code'] == course_code,
                request.session['course_sections']
            ))

            timeout = False

            for section in course_sections:
                """Checks if `section`'s timeslots collides with `x`"""
                def is_not_within_range(x) -> bool:
                    course_days = set(list(''.join(list(section['timeslots'].keys()))))
                    x_days = set(list(''.join(list(x['timeslots'].keys()))))

                    for day in list(course_days.intersection(x_days)):
                        print(day)
                        course_start, course_end = get_start_and_end(section['timeslots'], day)
                        x_start, x_end = get_start_and_end(x['timeslots'], day)

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

                        for x in ([section] + list(dcp_section)):
                            print_dict(x)
                            
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
            course_sections = couple_lec_and_lab(get_all_sections(cleaned_search_query))

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

##------------------------------------------------------------------------------------------------------------------
##----------------------------------------------Generating Permutation------------------------------------------------
def generate_permutation_view(request):
        # Obtain sections of classes in DCP
        ##printing DCP sesections, pero note na need mo muna mag add ng class bago mo to makita, cuz di sya nagsasave
        ##no work from fresh open i think, cuz cache to
        ## all sections to from dcp

        # Obtain all sections of courses in the DCP
        # -- guaranteed to be nonempty
        # -- already filled in `homepage_view`
        dcp_sections = request.session['dcp_sections']
        
        if 'schedule_permutations' not in request.session:
            request.session['schedule_permutations'] = []  # Initialize if not exists
        else:
            request.session['schedule_permutations'] = []


        student_id = request.user.id if request.user.is_authenticated else None
        saved_sched_ids = set()  # Store all saved schedule IDs

        if student_id:
            saved_sched_ids = set(SavedSchedule.objects.filter(student_id=student_id).values_list("sched_id", flat=True))


        count = 0
        for i, dcp_section in enumerate(list(product(*dcp_sections))):
            #check if dcp_section is not in SavedSchedules
            
            """
            if count in saved_sched_ids:  # Skip if schedule already saved
                count += 1
                continue
            """
            
            #check not conflicting
            if not is_conflicting(list(dcp_section)):

                schedule_entry = {
                    "sched_id": count,
                    "courses": tuple(fix_timeslots(course) for course in dcp_section)
                }

                request.session['schedule_permutations'].append(schedule_entry)

                count += 1
                #print(f"Schedule {count}")
                for x in (list(dcp_section)):
                    x.pop("course_title", None)
                    # dcp_section contains specific DICT section!
                    # 
                    
                    
                    #print_dict(x)
                    ...
                # print("\n")
                ## need nalang i save sa models 
                '''
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
                print(f"Sessions's dcp_sections now has {len(request.session['dcp_sections'])} sections.")
                print("EVERYCLASS IN THE DCP", request.session['dcp_sections'])
                messages.success(request, "Class has been successfully added.")
                return redirect(reverse('homepage_view'))


            '''
            if i == 100000:
                break
        
        print(" +++ SCHEDULE PERMUTATIONS START\n", request.session.get('schedule_permutations'), "\n +++ SCHEDULE PERMUTATIONS END")

        print(f"-- Found {count} schedules --")

        return redirect(reverse("homepage_view"))



def fix_timeslots(course):
    section_keys = list(course['section_name'].keys())  # Get keys from section_name
    timeslot_values = list(course.get('timeslots', {}).values())  # Get timeslot values
    venue_values = list(course.get('venue', {}).values())  # Get venue values

    # Convert timeslot values to tuples and align them with section_name keys
    course['timeslots'] = {
        section_keys[i]: tuple(timeslot_values[i]) if i < len(timeslot_values) else ()
        for i in range(len(section_keys))
    }

    # Align venue keys with section_name keys
    course['venue'] = {
        section_keys[i]: venue_values[i] if i < len(venue_values) else ""
        for i in range(len(section_keys))
    }

    return course

def view_sched_view(request, sched_id: int):
    #############################
    # For testing purposes only #
    #############################

    # Get the correct schedule based on sched_id
    schedule_permutations = request.session.get('schedule_permutations', [])
    selected_schedule = next((sched for sched in schedule_permutations if sched["sched_id"] == sched_id), None)

    #if selected_schedule is None:
        #return HttpResponse("Schedule not found", status=404)

    # Fix timeslots
    courses = tuple(fix_timeslots(course) for course in selected_schedule["courses"])

    if request.method == "POST" and "click_saved_sched" in request.POST:
        # Ensure user is logged in
        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to save schedules.")
            return redirect("login")

        student_id = request.user.id  # Get logged-in user's ID
        schedule_name = f"Sched {sched_id+1}"  # Generate a name

        # Check if this schedule already exists for the user
        saved_schedule, created = SavedSchedule.objects.get_or_create(
            student_id=student_id,
            sched_id=sched_id, 
            schedule_name=schedule_name,
            defaults={"is_saved": True},
        )
        
        for course in courses:
            # Check if a SavedCourse exists with the same course_details
            saved_course = SavedCourse.objects.filter(
                student_id=student_id,
                course_code=course["course_code"],
                course_details=course  # Ensures exact match on details
            ).first()

            if not saved_course:
                # Create a new SavedCourse if no exact match is found
                saved_course = SavedCourse.objects.create(
                    student_id=student_id,
                    course_code=course["course_code"],
                    course_details=course
                )

            saved_schedule.courses.add(saved_course)  # Add the correct SavedCourse
            

        messages.success(request, f"Schedule {sched_id+1} saved successfully!")
        return redirect("homepage_view")

    classes = [
        Course(
            course_code=course['course_code'],
            section_name=course['section_name'],
            capacity=course['capacity'],
            demand=course['demand'],
            units=course['units'],
            class_days=course['class_days'],
            location=course['location'],
            venue=course['venue'],
            instructor_name=course['instructor_name'],
            timeslots=course['timeslots'],
            offering_unit=course['offering_unit']
        )
        for course in courses
    ]

    main_table, export_table = generate_timetable(classes)

    context = {
        "sched_id": sched_id,
        "main_table": main_table,
        "export_table": export_table,
        "courses": classes,
        "units": f"{sum([course.units for course in classes])} units",
        "show_save_button": True,
    }

    return render(request, "view_sched.html", context)


def add_course_to_sched_view(request, sched_id: int):
    cs180 = Course(
        course_code="CS 180",
        section_name={"lec":"THR"},
        capacity=30,
        demand=30,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"}, venue={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"ROSELYN GABUD"},
        timeslots={"lec":(600,780)},
        offering_unit="DCS"
    )

    cs145 = Course(
        course_code="CS 145",
        section_name={"lec":"HONOR", "lab":"HONOR 2"},
        capacity=30,
        demand=1,
        units=4.0,
        class_days={"lec":"TH","lab":"M"},
        location={"lec":"Accenture","lab":"TL2"}, venue={"lec":"Accenture","lab":"TL2"},
        # coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"WILSON TAN", "lab":"GINO SAMPEDRO"},
        timeslots={"lec":(450,540), "lab":(240,420)},
        offering_unit="DCS"
    )

    cs192 = Course(
        course_code="CS 192",
        section_name={"lec":"TDE2/HUV2", "lab":"TDE2/HUV2"},
        capacity=30,
        demand=1,
        units=3.0,
        class_days={"lec":"T", "lab":"H"},
        location={"lec":"AECH", "lab":"AECH"}, venue={"lec":"AECH", "lab":"AECH"},
        # coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"ROWENA SOLAMO", "lab":"ROWENA SOLAMO"},
        timeslots={"lec":(180,300), "lab":(180,360)},
        offering_unit="DCS"
    )

    lis51 = Course(
        course_code="LIS 51",
        section_name={"lec":"WFU"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"SOLAIR"}, venue={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"DRIDGE REYES"},
        timeslots={"lec":(90,270)},
        offering_unit="SLIS"
    )

    cs153 = Course(
        course_code="CS 153",
        section_name={"lec":"THW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"}, venue={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"PHILIP ZUNIGA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    cs132 = Course(
        course_code="CS 132",
        section_name={"lec":"WFW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"AECH"}, venue={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"PAUL REGONIA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    classes = [cs180, cs145, cs153, cs132, cs192]

    dummy_course_sections = [
        Course(
            course_code="Dummy",
            section_name={"lec":"WFW"},
            capacity=30, demand=1,
            units=3.0,
            class_days={"lec":days},
            location={"lec":"AECH"}, venue={"lec":"AECH"},
            # coords={"lec":(0,0)},
            instructor_name={"lec":"PAUL REGONIA"},
            timeslots={"lec":slot},
            offering_unit="DCS"
        ) for (days, slot) in [('M',(0,180)),('M',(420,600)), ('M',(600,780)), ('W',(600,780)), ('F',(600,780))]
    ]

    # Generate schedule tables
    main_table, _ = generate_timetable(classes)

    timetables = []
    for dummy_course in dummy_course_sections:
        table, _ = generate_timetable(classes + [dummy_course])
        timetables.append(table)

    context = {
        "sched_id": sched_id,
        "schedule_name": "Temp",
        "main_table": main_table,
        "timetables": timetables,
        "new_sections" : dummy_course_sections,
        # "export_table": export_table,
        "courses": classes,
        "units": f"{sum([course.units for course in classes])} units",
        "show_unsave_button": True,
    }

    return render(request, "sched_add_course.html", context)

def view_saved_sched_view(request, sched_id: int):

    if request.method == "POST" and "click_unsaved_sched" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to unsave schedules.")
            return redirect("login")

        student_id = request.user.id
        saved_schedule = SavedSchedule.objects.filter(student_id=student_id, sched_id=sched_id).first()

        if saved_schedule:
            saved_schedule.delete()
            messages.success(request, f"Schedule {sched_id+1} unsaved successfully!")

        return redirect("homepage_view")

    student_id = request.user.id  # Ensure the user is logged in
    
    # Fetch the saved schedule for this user
    saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=sched_id)

    # Retrieve all associated saved courses
    saved_courses = saved_schedule.courses.all()

    # Convert saved courses (JSONField) into Course objects
    classes = [
        Course(**course.course_details)  # Unpack the dictionary properly
        for course in saved_courses
    ]

    # Generate schedule tables
    main_table, export_table = generate_timetable(classes)

    context = {
        "sched_id": sched_id,
        "schedule_name": saved_schedule.schedule_name,
        "main_table": main_table,
        "export_table": export_table,
        "courses": classes,
        "units": f"{sum([course.units for course in classes])} units",
        "show_unsave_button": True,
    }

    return render(request, "view_sched.html", context)