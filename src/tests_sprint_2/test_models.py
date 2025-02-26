# This Test is to test the Models 
#-------------------------------------------------------------------------------

from django.test import TestCase
from courses.models import DesiredCourse, Course

class DesiredCourseModelTest(TestCase):

    def setUp(self):
        self.desired_course = DesiredCourse.objects.create(
            student_id=1,
            course_code="CS101"
        )

    def test_desired_course_creation(self):
        self.assertEqual(self.desired_course.student_id, 1)
        self.assertEqual(self.desired_course.course_code, "CS101")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            DesiredCourse.objects.create(
                student_id=1,
                course_code="CS101"
            )

class CourseDataclassTest(TestCase):

    def setUp(self):
        self.course = Course(
            course_code="CS101",
            course_title="Introduction to Computer Science",
            offering_unit="CS Department",
            units=3.0,
            timeslot="MWF 10-11AM",
            venue="Room 101",
            instructor="Dr. John Doe"
        )

    def test_course_creation(self):
        self.assertEqual(self.course.course_code, "CS101")
        self.assertEqual(self.course.course_title, "Introduction to Computer Science")
        self.assertEqual(self.course.offering_unit, "CS Department")
        self.assertEqual(self.course.units, 3.0)
        self.assertEqual(self.course.timeslot, "MWF 10-11AM")
        self.assertEqual(self.course.venue, "Room 101")
        self.assertEqual(self.course.instructor, "Dr. John Doe")
        
    def test_course_creation_wrong(self):
        # This test is intentionally wrong and should fail
        self.assertNotEqual(self.course.course_code, "CS102")
        self.assertNotEqual(self.course.course_title, "Advanced Computer Science")
        self.assertNotEqual(self.course.offering_unit, "Math Department")
        self.assertNotEqual(self.course.units, 4.0)
        self.assertNotEqual(self.course.timeslot, "TTh 2-3:30PM")
        self.assertNotEqual(self.course.venue, "Room 102")
        self.assertNotEqual(self.course.instructor, "Dr. Jane Smith")
        
class FalseCourseDataclassTest(TestCase):

    def setUp(self):
        self.course = Course(
            course_title="Introduction to Computer Science",
            offering_unit="CS Department",
            units=3.0,
            timeslot="MWF 10-11AM",
            venue="Room 101",
            instructor="Dr. John Doe"
        )
    def test_course_creation_invalid(self):
        # This test is intentionally wrong and should fail
        self.assertNotEqual(self.course.course_title, "CS101")
        
 