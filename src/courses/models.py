from django.db import models

# Create your models here.

""" Model for saved courses in a user's Desired Classes Pool """
class DesiredCourse(models.Model):
    student_id =    models.IntegerField(unique=True)
    course_code =   models.TextField(unique=True)
