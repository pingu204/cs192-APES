# This Test is to test the Models
# -------------------------------------------------------------------------------

from django.test import TestCase
from courses.models import DesiredCourse


class DesiredCourseModelTest(TestCase):
    def setUp(self):
        self.desired_course = DesiredCourse.objects.create(
            student_id=1, course_code="CS101"
        )

    def test_desired_course_creation(self):
        self.assertEqual(self.desired_course.student_id, 1)
        self.assertEqual(self.desired_course.course_code, "CS101")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            DesiredCourse.objects.create(student_id=1, course_code="CS101")
