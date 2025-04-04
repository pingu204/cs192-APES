from django import forms

class PreferencesForm(forms.Form):
    BREAK_UNITS = [
        ('minutes', 'Minutes'),
        ('hours', 'hours')
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

    class_days = forms.MultipleChoiceField(choices=DAYS)

    total_distance_per_day = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "id" : "inputDistance", 
                "class": "form-control margin-left-sm",
                "placeholder":"0",
            }
        )
    )

    total_probability = forms.FloatField()
    earliest_time = forms.ChoiceField()
    latest_time = forms.ChoiceField()
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

    min_break_unit = forms.ChoiceField(choices=BREAK_UNITS)
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
    max_break_unit = forms.ChoiceField(choices=BREAK_UNITS)
