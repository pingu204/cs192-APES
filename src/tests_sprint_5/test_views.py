from django.test import TestCase, Client
from django.urls import reverse
from preferences.forms import PreferencesForm


class ModifyPreferencesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "modify_preferences_view"
        )  # Update with the actual URL name if different

    def test_get_request_renders_form(self):
        """Test that a GET request renders the preferences form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preferences.html")
        self.assertIsInstance(response.context["form"], PreferencesForm)

    def test_post_valid_data_updates_preferences(self):
        """Test that a POST request with valid data updates session preferences."""
        valid_data = {
            "number_of_classes": 5,
            "class_days": ["M", "W", "F"],
            "total_distance_per_day": 10,
            "total_probability": 80.0,
            "earliest_time": "08:00 AM",
            "latest_time": "05:00 PM",
            "min_break": 15,
            "min_break_unit": "1",
            "max_break": 60,
            "max_break_unit": "1",
        }
        response = self.client.post(self.url, data=valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect to homepage
        self.assertIn("preferences", self.client.session)
        self.assertEqual(self.client.session["preferences"]["number_of_classes"], 5)
        self.assertEqual(
            self.client.session["preferences"]["earliest_time_display"], "08:00 AM"
        )

    def test_post_invalid_data_shows_errors(self):
        """Test that a POST request with invalid data shows form errors."""
        invalid_data = {
            "earliest_time": "05:00 PM",
            "latest_time": "08:00 AM",  # Invalid: earliest_time is later than latest_time
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertTemplateUsed(response, "preferences.html")
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn("latest_time", response.context["form"].errors)

    def test_get_request_with_saved_preferences(self):
        """Test that a GET request pre-fills the form with saved preferences."""
        session = self.client.session
        session["raw_preferences"] = {
            "number_of_classes": 3,
            "class_days": ["T", "H"],
            "total_distance_per_day": 5,
        }
        session.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "preferences.html")
        form = response.context["form"]
        self.assertEqual(form.initial["number_of_classes"], 3)
        self.assertEqual(form.initial["class_days"], ["T", "H"])
        self.assertEqual(form.initial["total_distance_per_day"], 5)
