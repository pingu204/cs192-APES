from django.db import models

from dataclasses import dataclass

# Create your models here.

""" Model for saved courses in a user's Desired Classes Pool """
class DesiredCourse(models.Model):
    student_id =    models.IntegerField()
    course_code =   models.TextField()

    # Ensures unique combination of `student_id` and `course_code`
    # Obtained from https://www.geeksforgeeks.org/how-to-define-two-fields-unique-as-couple-in-django/
    class Meta():
        unique_together = ('student_id', 'course_code')

@dataclass
class Course():
    course_code: str
    course_title: str
    offering_unit: str
    units: float
    timeslot: str
    venue: str
    instructor: str
