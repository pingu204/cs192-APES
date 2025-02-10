from django.contrib import admin

from .models import Student

# APES Database re-configuration
admin.site.site_header = "APES Administration"
admin.site.index_title = "APES Admin Portal"


# Register your models here.

# Affixed Student User view in backend, hence the decorator @admin.register(Student)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff')
    ordering = ('email',)
    search_fields = ('username',)