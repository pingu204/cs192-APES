from django import forms
from django.shortcuts import get_object_or_404
import os, pandas as pd
from .models import DesiredCourse, SavedSchedule
from scraper.scrape import get_all_sections
from apes import settings

def get_cleaned_course_code(raw_code: str):
    return (' '.join(raw_code.split()))

class DesiredClassesForm(forms.Form):
    course_code = forms.CharField(
        label="Course Code",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter Class Code (e.g. 'Eng 13', 'PE 2 STD')",
                "class": "form-control",
            }
        ),
    )

    # Add init method to accept request and sched_id
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)  # Get request if passed
        self.sched_id = kwargs.pop("sched_id", None)  # Get sched_id if passed
        super().__init__(*args, **kwargs)

    """ Checks if `course_code` exists in the CSV file -> Valid """
    def clean_course_code(self):
        print("checking!")
        raw_course_code = self.cleaned_data.get("course_code")
        course_code = get_cleaned_course_code(raw_course_code)
        path = os.path.join(settings.BASE_DIR, "scraper", "csv", "courses.csv")
        courses = pd.read_csv(path)
        courselist = (courses["course_code"].tolist())

        # If we pass both the request and sched_id (occurs when adding a class...)
        if self.request is not None and self.sched_id is not None: # +1 since sched_id first index is 0 and 0 is a Falsy value so need to +1 in the case that its the first sched
            student_id = self.request.user.id
            saved_schedule = get_object_or_404(SavedSchedule, student_id=student_id, sched_id=self.sched_id)
            usercourselist = [course.course_code.lower() for course in saved_schedule.courses.all()]

            # Check if course is already saved
            if course_code.lower() in usercourselist:
                raise forms.ValidationError("Course already in the saved schedule. Try redrawing the course instead.")
        #usercourselist = [course.course_code for course in saved_schedule.courses.all()]
        
        # If searched query in ADDING A COURSE TO A SAVED SCHEDULE is already in the saved schedule, raise validation error
        # if user is doing this, should have opted to redraw a class instead...
        #if(course_code in usercourselist):
            #raise forms.ValidationError("Course already in the saved schedule. Try redrawing the course instead.")

        # UC3-S4
        if (course_code.upper() not in courselist and course_code.capitalize() not in courselist) and (not any(course.startswith(course_code.upper()) for course in courselist) and not any(course.startswith(course_code.capitalize()) for course in courselist)):
            raise forms.ValidationError("Class does not exist. Try checking if the entered class code is correct.")

        # Class is not yet offered in the semester
        if get_all_sections(get_cleaned_course_code(course_code)) == []:
            raise forms.ValidationError("No available classes yet. Try coming back later!")

        return course_code

    """ Checks if `course_code` is offered in the current semester """
    """ def clean_offered_course_code(self):
        print("checking din!")
        course_code = self.cleaned_data.get("course_code")

        

        return course_code """
