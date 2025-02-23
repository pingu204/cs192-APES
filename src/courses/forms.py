from django import forms

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