from django.db import models


class College(models.Model):

    COLLEGE_TYPE_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Deemed', 'Deemed'),
    ]

    college_name = models.CharField(max_length=200)

    location = models.CharField(max_length=150)

    state = models.CharField(max_length=100)

    college_type = models.CharField(
        max_length=20,
        choices=COLLEGE_TYPE_CHOICES
    )

    website = models.URLField(blank=True)

    annual_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.college_name