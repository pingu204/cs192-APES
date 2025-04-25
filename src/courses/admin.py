from django.contrib import admin

from .models import DesiredCourse, SavedCourse, SavedSchedule

# Register your models here.
admin.site.register(DesiredCourse)
admin.site.register(SavedCourse)
admin.site.register(SavedSchedule)
