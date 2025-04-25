from django.test import TestCase
from courses.models import SavedCourse, SavedSchedule


from django.db import IntegrityError


class SavedCourseModelTest(TestCase):
    def setUp(self):
        self.saved_course = SavedCourse.objects.create(
            student_id=1,
            course_code="CS101",
            course_details={"title": "Introduction to Computer Science", "units": 3},
        )

    def test_saved_course_creation(self):
        self.assertEqual(self.saved_course.student_id, 1)
        self.assertEqual(self.saved_course.course_code, "CS101")
        self.assertEqual(
            self.saved_course.course_details,
            {"title": "Introduction to Computer Science", "units": 3},
        )


class SavedScheduleModelTest(TestCase):
    def setUp(self):
        self.saved_course = SavedCourse.objects.create(
            student_id=1,
            course_code="CS101",
            course_details={"title": "Introduction to Computer Science", "units": 3},
        )
        self.saved_schedule = SavedSchedule.objects.create(
            student_id=1,
            sched_id=1,  # Ensure sched_id is set
            schedule_name="Fall 2025",
            is_saved=True,
        )
        self.saved_schedule.courses.add(self.saved_course)

    def test_saved_schedule_creation(self):
        self.assertEqual(self.saved_schedule.student_id, 1)
        self.assertEqual(self.saved_schedule.sched_id, 1)  # Check sched_id
        self.assertEqual(self.saved_schedule.schedule_name, "Fall 2025")
        self.assertTrue(self.saved_schedule.is_saved)
        self.assertIn(self.saved_course, self.saved_schedule.courses.all())

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            SavedSchedule.objects.create(
                student_id=1,
                sched_id=1,  # Ensure sched_id is set
                schedule_name="Fall 2025",
                is_saved=True,
            )

    def test_str_method(self):
        self.assertEqual(str(self.saved_schedule), "Fall 2025 (Student ID: 1)")

    def test_add_multiple_courses(self):
        course2 = SavedCourse.objects.create(
            student_id=1,
            course_code="CS102",
            course_details={"title": "Data Structures", "units": 3},
        )
        self.saved_schedule.courses.add(course2)
        self.assertIn(course2, self.saved_schedule.courses.all())
