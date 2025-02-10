from django.contrib import admin

from .models import Student

# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff')
    ordering = ('email',)
    search_fields = ('username',)