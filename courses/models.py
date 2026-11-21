from django.db import models


class Course(models.Model):

    course_name = models.CharField(max_length=150)

    course_category = models.CharField(max_length=100)

    minimum_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    duration_years = models.PositiveIntegerField(default=3)

    course_description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name