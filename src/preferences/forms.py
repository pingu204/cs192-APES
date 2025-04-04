from django import forms
from datetime import datetime, timedelta

def generate_time_choices():
    
    choices = [("--", "--")]
    current_time = datetime.strptime("07:00 AM", "%I:%M %p")  # Start at midnight
    end_time = datetime.strptime("10:00 PM", "%I:%M %p")  # Last selectable time

    while current_time <= end_time:
        formatted_time = current_time.strftime("%I:%M %p")  # 12-hour format with AM/PM
        choices.append((formatted_time, formatted_time))  # Store and display same value
        current_time += timedelta(minutes=15)  # Increment by 15 minutes
    print(choices)
    return choices

    # Assisted by Microsoft Copilot
    # Date: 04/05/2025
    # Prompt: can i generate a list of times in increments of 15 minutes, not in military time, as choices for a Django form
    # Changes made: changed the start time to 7:30 AM and end time to 10:00 PM

class PreferencesForm(forms.Form):
    BREAK_UNITS = [
        ('', '--'),
        ('1', 'minutes'),
        ('60', 'hours')
    ]
    DAYS = [
        ('Monday', 'M'),
        ('Tuesday', 'T'),
        ('Wednesday', 'W'),
        ('Thursday', 'Th'),
        ('Friday', 'F'),
        ('Saturday', 'S')
    ]
    
    number_of_classes = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "id" : "inputNumClasses", 
                "class": "form-control",
                "placeholder":"0",
                "min":"0",
                "max":"30",
            }
        )
    )

    class_days = forms.MultipleChoiceField(
        choices=DAYS,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class":"btn-check",
                "autocomplete":"off",
            }
        )

        )

    total_distance_per_day = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "id" : "inputDistance", 
                "class": "form-control margin-left-sm",
                "placeholder":"0",
            }
        )
    )

    total_probability = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "id" : "inputProbability", 
                "class": "form-control",
                "value":"0.00",
            }
        )
    )
    earliest_time = forms.ChoiceField(
        choices=generate_time_choices(), 
        initial="--",
        widget=forms.Select(
            attrs={
                "id" : "inputEarliestTime", 
                "class": "form-select form-control",
            }
        ))

    latest_time = forms.ChoiceField(
        choices=generate_time_choices(), 
        initial="--",
        widget=forms.Select(
            attrs={
                "id" : "inputLatestTime", 
                "class": "form-select form-control",
            }
        ))
    min_break = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "id" : "inputMinBreak", 
                "class": "form-control",
                "min":"0",
                "placeholder":"0",
            }
        )
    )

    min_break_unit = forms.ChoiceField(
        choices=BREAK_UNITS,
        initial="--",
        widget=forms.Select(
            attrs={
                "id" : "inputMinBreakUnit", 
                "class": "form-select form-control",
                "style": "flex: 0 0 fit-content;",
            }
        ))
    max_break = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
               "id" : "inputMaxBreak", 
                "class": "form-control",
                "min":"0",
                "placeholder":"0", 
            }
        )
    )
    max_break_unit = forms.ChoiceField(
        choices=BREAK_UNITS,
        initial="--",
        widget=forms.Select(
            attrs={
                "id" : "inputMaxBreakUnit", 
                "class": "form-select form-control",
                "style": "flex: 0 0 fit-content;",
            }
    ))
