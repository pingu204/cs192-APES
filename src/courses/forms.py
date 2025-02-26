from django import forms
import os, pandas as pd
from .models import DesiredCourse
from scraper.scrape import get_all_sections
from apes import settings

def get_cleaned_course_code(raw_code: str):
    return (' '.join(raw_code.split()))

class DesiredClassesForm(forms.Form):
    course_code = forms.CharField(
        label = "Course Code",
        widget = forms.TextInput(
            attrs = {
                "placeholder" : "Enter Class Code (e.g. \'Eng 13\', \'PE 2 STD\')",
                "class" : "form-control"
            }
        )
    )

    """ Checks if `course_code` exists in the CSV file -> Valid """
    def clean_course_code(self):
        print("checking!")
        raw_course_code = self.cleaned_data.get("course_code")
        course_code = get_cleaned_course_code(raw_course_code)
        path = os.path.join(settings.BASE_DIR, "scraper", "csv", "courses.csv")
        courses = pd.read_csv(path)
        courselist = (courses["course_code"].tolist())

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
