from django.db import models


# Create your models here.

""" Model for saved courses in a user's Desired Classes Pool """


class DesiredCourse(models.Model):
    student_id = models.IntegerField()
    course_code = models.TextField()

    # Ensures unique combination of `student_id` and `course_code`
    # Obtained from https://www.geeksforgeeks.org/how-to-define-two-fields-unique-as-couple-in-django/
    class Meta:
        unique_together = ("student_id", "course_code")


""" Model for saved courses in a user's Saved Courses in the schedule"""


class SavedCourse(models.Model):
    student_id = models.IntegerField()
    course_code = models.TextField()
    course_details = models.JSONField()  ##complete dict of the course


""" Model for saved schedules in a user's account """


class SavedSchedule(models.Model):
    student_id = models.IntegerField()
    sched_id = models.IntegerField()
    schedule_name = models.CharField(max_length=100)
    is_saved = models.BooleanField(
        default=False
    )  # gagawen true if complete yung dcp sched gagawen true
    courses = models.ManyToManyField(
        SavedCourse, related_name="schedules"
    )  ##complete dict of the course
    preferences = models.JSONField(
        default=dict, blank=True
    )  ##complete dict to save preferences; default to empty initially

    class Meta:
        unique_together = ("student_id", "schedule_name")

    def __str__(self):
        return f"{self.schedule_name} (Student ID: {self.student_id})"
