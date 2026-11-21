from django.db import models
from students.models import StudentProfile
from courses.models import Course
from colleges.models import College


class AdmissionApplication(models.Model):

    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Submitted', 'Submitted'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE
    )

    application_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Not Started'
    )

    application_deadline = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.college.college_name}"