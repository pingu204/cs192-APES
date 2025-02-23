from django.db import models

# Create your models here.

""" Model for saved courses in a user's Desired Classes Pool """
class DesiredCourse(models.Model):
    student_id =    models.IntegerField()
    course_code =   models.TextField()

    # Ensures unique combination of `student_id` and `course_code`
    class Meta():
        unique_together = ('student_id', 'course_code')
