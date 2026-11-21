
from django.contrib import admin
from .models import College, Department, CollegeCourse


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = (
        'college_name',
        'location',
        'state',
        'college_type',
        'is_verified',
        'verified_on',
        'is_active'
    )

    list_filter = ('college_type', 'is_verified', 'is_active')
    search_fields = ('college_name', 'location', 'state')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'department_name',
        'college',
        'is_verified',
        'verified_on',
        'is_active'
    )

    list_filter = ('is_verified', 'is_active', 'college')
    search_fields = ('department_name', 'college__college_name')


@admin.register(CollegeCourse)
class CollegeCourseAdmin(admin.ModelAdmin):
    list_display = (
        'college',
        'department',
        'course',
        'fee_amount',
        'fee_period',
        'academic_year',
        'is_verified',
        'is_active'
    )

    list_filter = (
        'academic_year',
        'fee_period',
        'is_verified',
        'is_active'
    )

    search_fields = (
        'college__college_name',
        'department__department_name',
        'course__course_name'
    )
