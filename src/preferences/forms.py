from django import forms
from datetime import datetime, timedelta


def generate_time_choices():
    # Generate time choices in increments of 15 minutes from 07:00 AM to 10:00 PM
    choices = [("", "--")]
    current_time = datetime.strptime("07:00 AM", "%I:%M %p")  # Start at 7:00 AM
    end_time = datetime.strptime(
        "10:00 PM", "%I:%M %p"
    )  # Last selectable time (10:00 PM)

    while current_time <= end_time:
        formatted_time = current_time.strftime("%I:%M %p")  # 12-hour format with AM/PM
        choices.append((formatted_time, formatted_time))  # Store and display same value
        current_time += timedelta(minutes=15)  # Increment by 15 minutes

    # print(choices)
    return choices

    # Assisted by Microsoft Copilot
    # Date: 04/05/2025
    # Prompt: can i generate a list of times in increments of 15 minutes, not in military time, as choices for a Django form
    # Changes made: changed the start time to 7:30 AM and end time to 10:00 PM


time_choices = generate_time_choices()


class PreferencesForm(forms.Form):
    # Units for break times
    BREAK_UNITS = [("", "--"), ("1", "minutes"), ("60", "hours")]

    # Days of the week options
    DAYS = [("M", "M"), ("T", "T"), ("W", "W"), ("H", "H"), ("F", "F"), ("S", "S")]

    number_of_classes = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "inputNumClasses",
                "class": "form-control",
                "placeholder": "0",
                "min": "0",
                "max": "30",
            }
        ),
    )

    class_days = forms.MultipleChoiceField(
        required=False, choices=DAYS, widget=forms.CheckboxSelectMultiple()
    )

    total_distance_per_day = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "inputDistance",
                "class": "form-control margin-left-sm",
                "placeholder": "0",
                "min": "0",
            }
        ),
    )

    total_probability = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "inputProbability",
                "class": "form-control",
                "placeholder": "0",
                "min": "0.00",
                "max": "100.00",
            }
        ),
    )

    earliest_time = forms.ChoiceField(
        required=False,
        choices=time_choices,
        initial="--",
        widget=forms.Select(
            attrs={
                "id": "inputEarliestTime",
                "class": "form-select form-control",
                "placeholder": "",
            }
        ),
    )

    latest_time = forms.ChoiceField(
        required=False,
        choices=time_choices,
        initial="--",
        widget=forms.Select(
            attrs={
                "id": "inputLatestTime",
                "class": "form-select form-control",
                "placeholder": "",
            }
        ),
    )

    min_break = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "inputMinBreak",
                "class": "form-control",
                "min": "0",
                "placeholder": "0",
            }
        ),
    )

    min_break_unit = forms.ChoiceField(
        required=False,
        choices=BREAK_UNITS,
        initial="--",
        widget=forms.Select(
            attrs={
                "id": "inputMinBreakUnit",
                "class": "form-select form-control",
                "style": "flex: 0 0 fit-content;",
                "autocomplete": "off",
                "autocorrect": "off",
                "autocapitalize": "off",
            }
        ),
    )

    max_break = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "inputMaxBreak",
                "class": "form-control",
                "min": "0",
                "placeholder": "0",
            }
        ),
    )

    max_break_unit = forms.ChoiceField(
        required=False,
        choices=BREAK_UNITS,
        initial="--",
        widget=forms.Select(
            attrs={
                "id": "inputMaxBreakUnit",
                "class": "form-select form-control",
                "style": "flex: 0 0 fit-content;",
                "autocomplete": "off",
                "autocorrect": "off",
                "autocapitalize": "off",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        earliest_time = cleaned_data.get("earliest_time")
        latest_time = cleaned_data.get("latest_time")

        # Check if earliest_time is before latest_time
        if earliest_time != "" and latest_time != "":
            earliest_index = next(
                (
                    index
                    for index, value in enumerate(time_choices)
                    if value[0] == earliest_time
                ),
                None,
            )
            latest_index = next(
                (
                    index
                    for index, value in enumerate(time_choices)
                    if value[0] == latest_time
                ),
                None,
            )

            if (
                earliest_index is not None
                and latest_index is not None
                and earliest_index >= latest_index
            ):
                self.add_error(
                    "latest_time", "Earliest time must be earlier than latest time."
                )

        # Now handle min_break and max_break validations
        min_break = cleaned_data.get("min_break")
        max_break = cleaned_data.get("max_break")
        min_break_unit = cleaned_data.get("min_break_unit")
        max_break_unit = cleaned_data.get("max_break_unit")

        # Check if the units for min_break and max_break are different
        if (
            min_break_unit != ""
            and max_break_unit != ""
            and min_break_unit == "60"
            and max_break_unit == "1"
        ):
            self.add_error(
                "min_break_unit", "Minimum break cannot be greater than maximum break."
            )

        # Check if min_break is greater than max_break (both should be in the same unit)
        if (
            min_break_unit != ""
            and max_break_unit != ""
            and min_break_unit == max_break_unit
        ):
            if min_break > max_break:
                self.add_error(
                    "min_break", "Minimum break cannot be greater than maximum break."
                )
            else:
                pass

        return cleaned_data
