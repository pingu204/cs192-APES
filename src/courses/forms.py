from django import forms
import os, pandas as pd
from .models import DesiredCourse

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

    def clean_course_code(self):
        raw_course_code = self.cleaned_data.get("course_code")
        course_code = (' '.join(raw_course_code.split()))
        path = '../src/scraper/csv/courses.csv'
        courses = pd.read_csv(path)
        courselist = (courses["course_code"].tolist())

        # UC3-S4
        if (course_code.upper() not in courselist and course_code.capitalize() not in courselist) and (not any(course.startswith(course_code.upper()) for course in courselist) and not any(course.startswith(course_code.capitalize()) for course in courselist)):
            raise forms.ValidationError("Class does not exist. Try checking if the entered class code is correct.")

        return course_code