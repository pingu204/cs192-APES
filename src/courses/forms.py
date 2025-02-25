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
        print("hello!")
        raw_course_code = self.cleaned_data.get("course_code")
        course_code = (' '.join(raw_course_code.split())).upper()
        cwd = os.path.dirname(__file__)
    
        # Navigate up one directory level
        relative_path = os.path.join(cwd, '..', 'scraper', 'csv', 'courses.csv')
        
        # Resolve the relative path to an absolute path
        absolute_path = os.path.abspath(relative_path)
        courses = pd.read_csv(absolute_path)
        # print(courses)
        courselist = (courses["course_code"].tolist())
        print("HEY")
        if course_code not in courselist: # UC3-S4 
            raise forms.ValidationError("Class does not exist. Try checking if the entered class code is correct.")
            # print(messages.error(request, "Class does not exist. Try checking if the entered class code is correct."))
            # form.error(request, "Class does not exist. Try checking if the entered class code is correct.")
        return course_code