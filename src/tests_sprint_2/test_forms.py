from django.test import TestCase
from courses.forms import DesiredClassesForm
from unittest.mock import patch, MagicMock


class DesiredClassesFormTest(TestCase):
    @patch("courses.forms.pd.read_csv")
    @patch("courses.forms.get_all_sections")
    def test_clean_course_code_valid(self, mock_get_all_sections, mock_read_csv):
        mock_read_csv.return_value = MagicMock()
        mock_read_csv.return_value["course_code"].tolist.return_value = [
            "ENG 13",
            "PE 2 STD",
        ]
        mock_get_all_sections.return_value = ["Section 1", "Section 2"]

        form = DesiredClassesForm(data={"course_code": "ENG 13"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["course_code"], "ENG 13")

    @patch("courses.forms.pd.read_csv")
    @patch("courses.forms.get_all_sections")
    def test_clean_course_code_invalid_not_exist(
        self, mock_get_all_sections, mock_read_csv
    ):
        mock_read_csv.return_value = MagicMock()
        mock_read_csv.return_value["course_code"].tolist.return_value = [
            "ENG 13",
            "PE 2 STD",
        ]
        mock_get_all_sections.return_value = ["Section 1", "Section 2"]

        form = DesiredClassesForm(data={"course_code": "MATH 101"})
        self.assertFalse(form.is_valid())
        self.assertIn("course_code", form.errors)
        self.assertEqual(
            form.errors["course_code"][0],
            "Class does not exist. Try checking if the entered class code is correct.",
        )

    @patch("courses.forms.pd.read_csv")
    @patch("courses.forms.get_all_sections")
    def test_clean_course_code_no_available_classes(
        self, mock_get_all_sections, mock_read_csv
    ):
        mock_read_csv.return_value = MagicMock()
        mock_read_csv.return_value["course_code"].tolist.return_value = [
            "ENG 13",
            "PE 2 STD",
        ]
        mock_get_all_sections.return_value = []

        form = DesiredClassesForm(data={"course_code": "ENG 13"})
        self.assertFalse(form.is_valid())
        self.assertIn("course_code", form.errors)
        self.assertEqual(
            form.errors["course_code"][0],
            "No available classes yet. Try coming back later!",
        )
