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
    number_of_classes = forms.IntegerField()
    class_days = forms.MultipleChoiceField(choices=DAYS)
    total_distance_per_day = forms.IntegerField()
    total_probability = forms.FloatField()
    earliest_time = forms.ChoiceField()
    latest_time = forms.ChoiceField()
    min_break = forms.IntegerField()
    min_break_unit = forms.ChoiceField(choices=BREAK_UNITS)
    max_break = forms.IntegerField()
    max_break_unit = forms.ChoiceField(choices=BREAK_UNITS)
