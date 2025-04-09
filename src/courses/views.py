from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import DesiredClassesForm
from django import forms
import csv
import os
from .models import DesiredCourse
from dataclasses import asdict
from scraper.scrape import get_all_sections, couple_lec_and_lab, print_dict
from .misc import get_unique_courses, is_conflicting, get_start_and_end
from apes import settings
from .schedule import Course, generate_timetable, get_time
from apes.utils import get_course_details_from_csv
import json
import ast 
from collections import defaultdict

from courses.models import SavedSchedule, SavedCourse

from itertools import product
import numpy as np
import pandas as pd
from django.contrib import messages

import copy

def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm(request.GET, request=request)

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
            print("COURSE SECTIONS: ", course_sections)  # Debugging
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
        form = DesiredClassesForm(request.GET, request=request)

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

        #if dcp_sections == []:
            #return redirect(reverse("homepage_view"))

        print("DCP SECTIONS: ", dcp_sections)  # Debugging
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
            if not is_conflicting(list(dcp_section)):

                #print("DCP SECTION SAMPLE", dcp_section)

                schedule_entry = {
                    "sched_id": count,
                    "courses": dcp_section,
                    "number_of_classes_per_day": {},
                    "class_times": []
                }

                #print("CLASS TIMES", schedule_entry['courses'][0]['timeslots'].values())

                #print("MAXIMUM NBR OF CLASS", request.session['preferences']['number_of_classes'])

                # only add a schedule to a permutation if it HAS ATLEAST 1 CLASS
                # if CLEAR -> GENERATE; must generate NO PERMUTATIONS

                # loop for adding a number_of_classes_per_day key (counter) for each schedule generated
                for course in schedule_entry['courses']:
                    # print(course)
                    for day in list(course['class_days'].values()):
                        days_list = list(day)
                        for dayz in days_list:
                            if dayz in schedule_entry['number_of_classes_per_day']:
                                schedule_entry['number_of_classes_per_day'][dayz] += 1
                            else:
                                schedule_entry['number_of_classes_per_day'][dayz] = 1

                    for timeslot in list(course['timeslots'].values()):
                        schedule_entry['class_times'] += timeslot

                schedule_entry['class_times'].sort()

                # print(schedule_entry['number_of_classes_per_day'])
                # print(schedule_entry['number_of_classes_per_day'].values())

                # print_dict(schedule_entry)
                
                # only add a schedule to a permutation if it HAS ATLEAST 1 CLASS
                if len(schedule_entry['courses']) != 0:
                    # Cross-check the schedule against each *enabled* preference
                    # -- ignore if it doesn't satisfy AT LEAST ONE
                    # -- add to valid schedules if it satisfies ALL
                    if 'preferences' in request.session:
                        
                        # +-- MAX NUMBER OF CLASSES PER DAY --+
                        # Check if the number of classes per day is <= `number_of_classes`
                        if request.session['preferences']['number_of_classes']:
                            if not all(x <= request.session['preferences']['number_of_classes'] for x in list(schedule_entry['number_of_classes_per_day'].values())): 
                                continue
                        
                        # +-- CLASS DAYS --+
                        # Check if the schedule's class days is a subset of `class_days`
                        if request.session['preferences']['class_days']:
                            # if days in generated scheds is NOT a subset of the chosen class_days by the user, then, SKIP and dont add to sched permutation
                            if not set(list(schedule_entry['number_of_classes_per_day'].keys())) <= set(request.session['preferences']['class_days']):
                                continue
                        
                        # +-- TOTAL DISTANCE --+
                        # Check if total travel distance per day is <= `total_distance_per_day`
                        if request.session['preferences']['total_distance_per_day']:
                            # max_dist = get_max_distance(schedule_entry['courses'])
                            dists_per_day = get_distance_per_day(schedule_entry['courses'])
                            # print(dists_per_day)
                            if max(dists_per_day) > request.session['preferences']['total_distance_per_day']:
                                continue
                            # if max_dist > request.session['preferences']['total_distance_per_day']:
                            #     continue

                        # +-- CLASS TIMES --+
                        # Check if earliest and latest class in the sched
                        # is within [`earliest_time`, `latest_time`]
                        if request.session['preferences']['earliest_time'] is not None and request.session['preferences']['latest_time'] is not None:
                            print(request.session['preferences']['earliest_time'])
                            print(request.session['preferences']['latest_time'])
                            print("Test")
                            if schedule_entry['class_times'][0] < request.session['preferences']['earliest_time'] or schedule_entry['class_times'][-1] > request.session['preferences']['latest_time']:
                                continue
                        
                        # +-- BREAK TIME DURATION --+
                        # Check if break time durations are within [`min_break`,`max_break`]
                        if request.session['preferences']['min_break'] is not None and request.session['preferences']['max_break'] is not None:
                            if request.session['preferences']['min_break'] > 0 or request.session['preferences']['max_break'] > 0:

                                # Obtain user preferences
                                min_break = request.session['preferences'].get('min_break', 0) 
                                max_break = request.session['preferences'].get('max_break', 0) 

                                # Case: only one course in the schedule
                                # -- (a) user needs a break
                                if (len(schedule_entry['courses']) == 1) and (min_break > 0):
                                    print("Invalid break found: only one course in schedule")
                                    continue
                                # -- (b) user doesn't need a break
                                elif (len(schedule_entry['courses']) == 1) and (min_break == 0):
                                    request.session['schedule_permutations'].append(schedule_entry)
                                    continue

                                # Group class times by day
                                class_times_by_day = defaultdict(list)
                                for course in schedule_entry['courses']:
                                    for section, days in course['class_days'].items():
                                        for day in days:
                                            class_times_by_day[day].extend(course['timeslots'].get(section, []))

                                # Sort class times for each day
                                for day in class_times_by_day:
                                    class_times_by_day[day].sort()

                                # Check breaks for each day
                                invalid_break_found = False
                                for day, times in class_times_by_day.items():

                                    if len(times) < 2:
                                        continue

                                    # Check if there's only one class in the day
                                    if len(times) == 2 and min_break > 0:
                                        print(f"Invalid break found on {day}: only one break")
                                        invalid_break_found = True
                                        break

                                    # Compute for the break times
                                    breaks = []
                                    for (prev_time, next_time) in zip(times, times[1:]):
                                        temp = next_time - prev_time
                                        if temp != 0:
                                            breaks.append(temp)
                                    
                                    print(f"Day: {day}, Class times: {times}, Breaks: {breaks}")

                                    # Check if minimum break time is less than user spec OR
                                    # if maximum break time is greater than user spec
                                    if min(breaks) < min_break or max(breaks) > max_break:
                                        print(f"Invalid breaks found on {day}: {breaks}")
                                        invalid_break_found = True
                                        break

                                # Skip the schedule if invalid breaks are found
                                if invalid_break_found:
                                    continue

                    
                    # Append schedule to valid permutations
                    request.session['schedule_permutations'].append(schedule_entry)

                count += 1
                
                for x in (list(dcp_section)):
                    x.pop("course_title", None)

            if i == 1000: 
                break

        return redirect(reverse("homepage_view"))

def get_distance_per_day(courses):
    """ Returns a list of the distances (in km) walked each day in a given schedule. """
    # print('courses: ', courses)
    # max_distance = 0.0
    distances_per_day = []
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
    # print('classes:')
    for day in ['M','T','W','H','F','S']:
        day_classes = []
        current_distance = 0.0
        for c in classes:
            for classType, d in c.class_days.items():
                # print('type:', classType, 'day:',  d)
                if day in d:
                    day_classes.append((c, c.location[classType], c.timeslots[classType]))
                    # print('day:', day, 'course_code:', c.course_code, 'location:', c.location[classType])
                    
        # print('day: ', day, day_classes)
        day_classes = sorted(day_classes, key=lambda x: x[2]) # sort by timeslot of the class
        
        if len(day_classes) <= 1:
            distances_per_day.append(0.0) # no distance to be computed.
            continue # only one class in that day, so no distance to be computed.
        # print('A,B:')
        for A, B in zip(day_classes, day_classes[1:]):
            # print(A[1], B[1])
            current_distance += get_distance(A[1], B[1])
        
        distances_per_day.append(current_distance/1000) # convert to km
    # print(max_distance)
    
    # return max_distance / 1000 # convert to km
    # print('distances_per_day:', distances_per_day)
    return distances_per_day

        

def get_distance(loc_A, loc_B):
    """ Given two course locations, refers to distance_pairs.csv to get the distance in meters between the two courses' locations.
        If the distance is not found, returns 0.0. """
    file_path = os.path.join(settings.BASE_DIR, "scraper", "csv", "distance_pairs.csv") 
    df = pd.read_csv(file_path)
    df.columns = ['endpts', 'distance_in_m']

    ref_table = dict(zip(df['endpts'], df['distance_in_m']))

    lookupAB = '(\'' + loc_A + '\', \'' + loc_B + '\')'
    lookupBA = '(\'' + loc_B + '\', \'' + loc_A + '\')'

    if ref_table.get(lookupAB):
        # print(ref_table[lookupAB])
        return float(ref_table[lookupAB])
    elif ref_table.get(lookupBA):
        # print(ref_table[lookupBA])
        return float(ref_table[lookupBA])
    else:
        # print("0.0")
        return 0.0

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


#viewing unsaved schedules
def view_sched_view(request, sched_id: int):
    #############################
    # For testing purposes only #
    #############################
    print("ViewSched")
    # Get the correct schedule based on sched_id
    schedule_permutations = request.session.get('schedule_permutations', [])
    selected_schedule = next((sched for sched in schedule_permutations if sched["sched_id"] == sched_id), None)

    #if selected_schedule is None:
        #return HttpResponse("Schedule not found", status=404)

    print("Unsaved Sched ID:", sched_id)

    # Fix timeslots
    #courses = tuple(fix_timeslots(course) for course in selected_schedule["courses"])
    courses = selected_schedule["courses"]

    if request.method == "POST" and "click_saved_sched" in request.POST:
        # Ensure user is logged in
        
        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to save schedules.")
            return redirect("login_view")

        student_id = request.user.id  # Get logged-in user's ID
        schedule_name = f"Sched {sched_id+1}"  # Generate a name

        # (1) if sched to save already in saved scheds, overwrite the old saved sched totally by deleting it first
        SavedSchedule.objects.filter(
            student_id=student_id,
            sched_id=sched_id
        ).delete()

        # Check if this schedule already exists for the user
        saved_schedule, _ = SavedSchedule.objects.get_or_create(
            student_id=student_id,
            sched_id=sched_id, 
            schedule_name=schedule_name,
            defaults={"is_saved": True},
        )
        
        preferences = request.session.get('preferences', {})
        saved_schedule.preferences = preferences
        saved_schedule.save()

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
        return redirect(reverse('homepage_view'))

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
        "session": request.session,
    }

    return render(request, "view_sched.html", context)


#viewing saved schedules
def view_saved_sched_view(request, sched_id: int):
    
    print("Saved Sched ID:", sched_id)

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


    # get the class to remove from what the user clicked in HTML; garnered from 'courses' in the context
    if request.method == "POST" and "class_to_remove" in request.POST:
        course_data_str = request.POST["class_to_remove"]

        # convert the returned course_data from view_sched.html to the correct dict
        course_data = eval(f"dict({course_data_str.replace('Course(', '').rstrip(')')})")

        # Get the course to remove
        course_to_remove = saved_schedule.courses.filter(course_code=course_data['course_code']).first() # based on course code instead of course_details

        # Check if course exists before removing
        if course_to_remove:
            if saved_schedule.courses.count() == 1:  # Only 1 course left
                saved_schedule.courses.remove(course_to_remove)  # Remove from the schedule

                if course_to_remove:  # Check if not None before deleting
                    course_to_remove.delete()  # Delete the course instance
                
                # Refresh the schedule from DB to update the courses relation
                saved_schedule.refresh_from_db()

                # Double-check if the schedule is empty after refresh
                if saved_schedule.courses.count() == 0:  # NOW IT WORKS!!!!!!!!!!!!
                    saved_schedule.delete()  # Delete the entire schedule
                    messages.success(request, f"Schedule {sched_id+1} unsaved successfully!")

                    # Redirect to homepage after removing the last course
                    return redirect(reverse("homepage_view"))
            
            else:
                saved_schedule.courses.remove(course_to_remove)  # Remove the course from schedule
                
                if course_to_remove:  # Check if not None before deleting
                    course_to_remove.delete()  # Delete the course instance
                    messages.success(request, "Class has been removed from the schedule.")
        else:
            # Placeholder for when the course is not found in the schedule
            messages.error(request, f"Course {course_data['course_code']} not found in the schedule.")
            pass  # Placeholder muna, please remove this @riana, thanks!

        # Redirect to view the schedule after removing the course
        return redirect("view_saved_sched_view", sched_id=sched_id)



    context = {
        "sched_id": sched_id,
        "schedule_name": saved_schedule.schedule_name,
        "main_table": main_table,
        "export_table": export_table,
        "courses": classes,
        "units": f"{sum([course.units for course in classes])} units",
        "show_unsave_button": True,
        "saved_schedules" : SavedSchedule.objects.filter(student_id=request.user.id),
    }

    return render(request, "view_sched.html", context)


def convert_timeslots_to_tuples(course):
    for key, value in course['timeslots'].items():
        if isinstance(value, list):
            course['timeslots'][key] = tuple(value)
    return course

def has_conflict(classes):
    """
    Check if there are any conflicting classes based on timeslots and days,
    including cases where courses may have multiple sections with separate times.
    
    Args:
        classes (list): List of class dictionaries, each containing 'timeslots' and 'class_days'.
        
    Returns:
        bool: True if there's a conflict, otherwise False.
    """
    
    # Loop through each day (M, T, W, H, F, S) to detect conflicts
    for day in "MTWHFS":
        # Store occupied time slots as intervals for each section on this day
        occupied_slots = []

        # Check each class in the list
        for course in classes:
            # Determine which sections (lec/lab/etc.) have classes on the given day
            timeslots = course.get("timeslots", {})
            class_days = course.get("class_days", {})
            
            for section, section_days in class_days.items():
                # If this section has a class on the current day
                if day in section_days:
                    # Retrieve the start and end times for the section's timeslot
                    timeslot = timeslots.get(section, ())
                    
                    if timeslot:  # Check only if the timeslot exists and isn't empty
                        start_time, end_time = timeslot

                        # Check for conflicts with already occupied time slots
                        for occupied_start, occupied_end in occupied_slots:
                            if not (end_time <= occupied_start or start_time >= occupied_end):
                                # If times overlap, there's a conflict
                                return True
                        
                        # Add the current class's time slot to the list of occupied slots
                        occupied_slots.append((start_time, end_time))
                    
    # If no conflicts are found after checking all classes
    return False

#adding course to saved schedule
def add_course_to_sched_view(request, sched_id: int):
    ##Already legit schedule na kinukuha not ung testing ni jopeth
    
    #get the schedule from database 
    student_id = request.user.id 
    
    saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=sched_id)
    
    saved_courses = saved_schedule.courses.all()
    classes = [
        convert_timeslots_to_tuples(course.course_details)  # Unpack the dictionary properly
        for course in saved_courses
    ]
    ##print("Classes: ", classes)
    
    #Form for the search
    search_results = []

    
    # add class to the saved schedule via "Add" button
    if request.method == "POST" and "course_data" in request.POST:
        course_data_str = request.POST["course_data"]

        # convert the returned course_data from sched_add_course.html to the correct dict
        course_data = eval(f"dict({course_data_str.replace("Course(", "").rstrip(")")})")

        #print("COURSE DATA STR", course_data)
        #print("COURSE DATA TYPE", type(course_data))

        # Add new course to SavedSchedule
        saved_course = SavedCourse.objects.create(
            student_id=student_id,
            course_code=course_data["course_code"],
            course_details=course_data
        )

        # Add course to the saved schedule
        saved_schedule.courses.add(saved_course)

        return redirect(reverse("view_saved_sched_view", kwargs={'sched_id':sched_id}))
    

    form = DesiredClassesForm(request.GET, request=request, sched_id=sched_id)
    raw_search_query = request.GET.get("course_code")
    if request.GET.get("course_code"):
        ##print("Raw Search Query: ", raw_search_query)
        #cleaning the search query
        cleaned_search_query = (' '.join(raw_search_query.split())).upper()


        # test and implementation if search query is already in the saved_courses; should not push thru:
        #print("  - CLEANED SEARCH ADD QUERY", cleaned_search_query, "TEST")
        #print("  - Saved courses course codes:", [course.course_code for course in saved_courses])

        #saved_courses_codes = [course.course_code for course in saved_courses]
        if form.is_valid():
            # Obtain all sections associated 
            course_sections = couple_lec_and_lab(get_all_sections(cleaned_search_query, strict=True)) 
            for c in course_sections:
                print_dict(c)
            temp = copy.deepcopy(course_sections)
            #course_sections = tuple(fix_timeslots(course) for course in course_sections)
            print("after")
            for i, c in enumerate(course_sections):
                print_dict(temp[i])
                print_dict(course_sections[i])
            # print("Course Sections: ", course_sections)
            for course in course_sections:
                #fix the scraping
                course['units'] = float(course['units'])
                del course['course_title'] 
                flat_classes = [course for sublist in classes for course in (sublist if isinstance(sublist, list) else [sublist])]
                flat_classes.append(course) #add the new course to the classes
                if not has_conflict(flat_classes): #newly created function on top of here
                    # print("Course OK: ", flat_classes)   
                    search_results.append(Course(**course)) #add the new course to the search results
                    flat_classes.pop() #remove the new course from the classes
            
    ## Search Results contain the classes non conflicting  ----> 
    ##print("Search Results: ", search_results)

    # Generate schedule tables
    # Get the saved Classes again para maging course sila ulet
    saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=sched_id)
    
    saved_courses = saved_schedule.courses.all()
    classes = [
        Course(**convert_timeslots_to_tuples(course.course_details))  # Unpack the dictionary properly
        for course in saved_courses
    ]
     # Generate schedule tables
    main_table, _ = generate_timetable(classes, glow_idx=len(classes))

    timetables = []
    timeslots = []
     # Generate schedule tables + the new class maybe here ung schedules
    for courses_result in search_results:

        table, _ = generate_timetable(classes + [courses_result], glow_idx=len(classes))
        timetables.append(table)

        course_timeslots = {}
        for classType, (start,end) in courses_result.timeslots.items():
            course_timeslots[classType] = f"{get_time(start)} - {get_time(end)}"
        timeslots.append(course_timeslots)
    
    context = {
        "sched_id": sched_id,
        "schedule_name": "Temp",
        "main_table": main_table,
        "timetables": timetables,
        "new_sections" : search_results,
        # "export_table": export_table,
        "courses": classes,
        "units": f"{sum([course.units for course in classes])} units",
        "show_unsave_button": True,
        "form": form,
        "search_results": zip(search_results, timeslots),
    }

    return render(request, "sched_add_course.html", context)






##----------------------REDRAW CLASS-----------------------------------##
def redraw_course_to_sched(request, sched_id: int, course_code: str):
    
    student_id = request.user.id 
    
    saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=sched_id)
    
    saved_courses = saved_schedule.courses.all()
    classes = [
        convert_timeslots_to_tuples(course.course_details)  # Unpack the dictionary properly
        for course in saved_courses
    ]
   
    # redraw class in the saved schedule via "Choose" button
    if request.method == "POST" and "course_data" in request.POST:
        course_data_str = request.POST["course_data"]

        # convert the returned course_data from sched_add_course.html to the correct dict
        course_data = eval(f"dict({course_data_str.replace("Course(", "").rstrip(")")})")

        # ensure and remove the course with the same course_code as the course we chose to redraw it with:
        existing_course = saved_schedule.courses.filter(course_code=course_data["course_code"]).first()

        # ensure if course we chose to redraw exists, delete it since we will redraw it with our chosen course via the "Choose" button
        if existing_course:
            saved_schedule.courses.remove(existing_course)
            existing_course.delete()

        #print("COURSE DATA STR", course_data)
        #print("COURSE DATA TYPE", type(course_data))

        # Add new course to SavedSchedule to replace the old one, effectively redrawing it
        saved_course = SavedCourse.objects.create(
            student_id=student_id,
            course_code=course_data["course_code"],
            course_details=course_data
        )

        # Add course to the saved schedule
        saved_schedule.courses.add(saved_course)

        return redirect(reverse("view_saved_sched_view", kwargs={'sched_id':sched_id}))

    ## GET THE COURSE DETAILS NG PINILI NA REDRAWN
    course_details = next((course for course in classes if course['course_code'] == course_code), None)
    if not course_details:
        messages.error(request, "Course not found.")
        return redirect("view_saved_sched_view", sched_id=sched_id)

    print("YOU ARE IN REDRAW")
    print("COURSE DETAILS: ", course_code)   
    
    #GET FROM CACHE UNG PERMUTATION NG CLASS
    schedule_permutations = []
    
    #remove the course_code class from the classes
    temp = [course for course in classes if course['course_code'] != course_code]
   
    #get all sections of the course_code
    course_sections = couple_lec_and_lab(get_all_sections(course_code, strict=True))
    #print("COURSE SECTIONS: ", course_sections)
    
    for c in course_sections:
        temp.append(c)
        if not has_conflict(temp):
            schedule_permutations.append(temp[:]) #[:] so the pop wont affect the schedule_permutations
        temp.pop()

    
    if not schedule_permutations:
        messages.error(request, "Schedule containing the specified course with different sections not found.")
        print("GO BACK")
        return redirect("view_saved_sched_view", sched_id=sched_id)

    # case where only orig class is part of the schedule_permutations; 
    # i.e., only sched permutation is the sched with the class we chose to redraw (1 sched)
    if len(schedule_permutations) <= 1:
        messages.error(request, "No available classes.")
        return redirect("view_saved_sched_view", sched_id=sched_id)
    
    #eto same na needed kasi ung Course class to the schedules for the time table
    saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=sched_id)
    saved_courses = saved_schedule.courses.all()
    classes = [
        Course(**convert_timeslots_to_tuples(course.course_details))  # Unpack the dictionary properly
        for course in saved_courses
    ]
    
    #eto naman changing lahat sa schedules to Course class (inside selected_schedules) 
    #redrawn_sched ung container for final na naka Course Class na, 
    redrawn_sched = []
    for courses in schedule_permutations:
        
        for course in courses:
            course['units'] = float(course['units'])
            course.pop('course_title', None)  # Remove the course_title key if it exists
        changed = [
            Course(**course) for course in courses
        ]
        redrawn_sched.append(changed)
    
    #eto ung filtering ng course_sections para sa redrawn_sched
    course_sections = filter_course_sections(course_sections, schedule_permutations)
    # print("Redrawn Schedule:", redrawn_sched)
    main_table, _ = generate_timetable(classes, glow_idx=len(classes))

    timetables = []
    timeslots = []
     # Generate schedule tables + the new class maybe here ung schedules di ko pa gets pano to sorry
    for redrawn_scheds in redrawn_sched:
        table, _ = generate_timetable(redrawn_scheds, glow_idx=len(redrawn_scheds)-1)
        print("REDRAWN SCHED", redrawn_scheds)
        timetables.append(table)
        
    course_sectionss = []
    for course in course_sections:
        course['units'] = float(course['units'])

        course_timeslots = {}
        for classType, (start,end) in course["timeslots"].items():
            course_timeslots[classType] = f"{get_time(start)} - {get_time(end)}"
        timeslots.append(course_timeslots)

        course.pop('course_title', None)  # Remove the course_title key if it exists
        course_sectionss.append(Course(**course))
    
    #print(schedule_permutations)
    #print("SCHEDPERMLEN", len(schedule_permutations))

    #print(redrawn_scheds)
    #print("REDRAWLEN", len(redrawn_scheds))
    
    #print(redrawn_sched)
    #print(len(redrawn_sched))

    context = {
        "sched_id": sched_id,
        "schedule_name": "Temp",
        "main_table": main_table,
        "timetables": timetables, 
        "redrawn_scheds" : zip(course_sectionss, timeslots),
        "schedule_permutations": schedule_permutations,
        "course_code" : course_code,
    }

    return render(request, "sched_redraw.html", context)

def filter_course_sections(course_sections, schedule_permutations):
    # Create a set of course codes and section names that are in the schedule_permutations
    valid_courses = set()
    for schedule in schedule_permutations:
        for course in schedule:
            valid_courses.add((course['course_code'], course['section_name']['lec']))
            if 'lab' in course['section_name']:
                valid_courses.add((course['course_code'], course['section_name']['lab']))

    # Filter course_sections to only include those in valid_courses
    filtered_sections = [
        course for course in course_sections
        if (course['course_code'], course['section_name']['lec']) in valid_courses or
           ('lab' in course['section_name'] and (course['course_code'], course['section_name']['lab']) in valid_courses)
    ]

    return filtered_sections