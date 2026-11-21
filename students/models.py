from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    STREAM_CHOICES = [
        ('Science', 'Science'),
        ('Commerce', 'Commerce'),
        ('Arts', 'Arts'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    education_stream = models.CharField(
        max_length=20,
        choices=STREAM_CHOICES,
        blank=True
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name