from django.test import TestCase
from preferences.forms import PreferencesForm


class PreferencesFormTests(TestCase):
    def test_valid_form(self):
        """Test that the form is valid with correct data."""
        form_data = {
            "number_of_classes": 5,
            "class_days": ["M", "W", "F"],
            "total_distance_per_day": 10,
            "total_probability": 0.8,
            "earliest_time": "08:00 AM",
            "latest_time": "05:00 PM",
            "min_break": 15,
            "min_break_unit": "1",
            "max_break": 60,
            "max_break_unit": "1",
        }
        form = PreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_earliest_and_latest_time(self):
        """Test that the form is invalid when earliest_time is later than latest_time."""
        form_data = {
            "earliest_time": "05:00 PM",
            "latest_time": "08:00 AM",
        }
        form = PreferencesForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["latest_time"][0],
            "Earliest time must be earlier than latest time.",
        )

    def test_invalid_min_break_greater_than_max_break(self):
        """Test that the form is invalid when min_break is greater than max_break."""
        form_data = {
            "min_break": 60,
            "min_break_unit": "1",
            "max_break": 30,
            "max_break_unit": "1",
        }
        form = PreferencesForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["min_break"][0],
            "Minimum break cannot be greater than maximum break.",
        )

    def test_invalid_min_break_unit_greater_than_max_break_unit(self):
        """Test that the form is invalid when min_break_unit is in hours and max_break_unit is in minutes."""
        form_data = {
            "min_break": 1,
            "min_break_unit": "60",  # hours
            "max_break": 30,
            "max_break_unit": "1",  # minutes
        }
        form = PreferencesForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["min_break_unit"][0],
            "Minimum break cannot be greater than maximum break.",
        )

    def test_valid_form_with_no_optional_fields(self):
        """Test that the form is valid when optional fields are left empty."""
        form_data = {
            "number_of_classes": 3,
            "class_days": ["T", "H"],
        }
        form = PreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_total_probability_out_of_range(self):
        """Test that the form is invalid when total_probability is out of range."""
        form_data = {
            "total_probability": 120.0,  # Exceeds 100%
        }
        form = PreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_number_of_classes_negative(self):
        """Test that the form is invalid when number_of_classes is negative."""
        form_data = {
            "number_of_classes": -1,
        }
        form = PreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_total_distance_negative(self):
        """Test that the form is invalid when total_distance_per_day is negative."""
        form_data = {
            "total_distance_per_day": -5,
        }
        form = PreferencesForm(data=form_data)
        self.assertTrue(form.is_valid())
