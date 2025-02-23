from django import forms

from .models import DesiredCourse

class DesiredClassesForm(forms.ModelForm):
    course_code = forms.TextField(
        required = True,
        label = "Course Code",
        widget = forms.TextInput(
            attrs = {
                "placeholder" : "Enter Class Code (e.g. \'Eng 13\', \'PE 2 STD\')"
            }
        )
    )