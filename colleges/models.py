
from django.db import models
from courses.models import Course


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

    # Official verification details
    college_source_url = models.URLField(blank=True)
    verified_on = models.DateField(
        null=True,
        blank=True
    )
    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.college_name


class Department(models.Model):

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='departments'
    )

    department_name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    source_url = models.URLField(blank=True)

    verified_on = models.DateField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'department_name'],
                name='unique_college_department'
            )
        ]

    def __str__(self):
        return f"{self.college.college_name} - {self.department_name}"


class CollegeCourse(models.Model):

    FEE_PERIOD_CHOICES = [
        ('Annual', 'Annual'),
        ('Semester', 'Semester'),
        ('Total', 'Total Course Fee'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='course_offerings'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_offerings'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='college_offerings'
    )

    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    fee_details = models.TextField(blank=True)

    fee_period = models.CharField(
        max_length=20,
        choices=FEE_PERIOD_CHOICES,
        default='Annual'
    )

    academic_year = models.CharField(max_length=9)

    shift = models.CharField(
        max_length=30,
        blank=True
    )

    source_url = models.URLField(blank=True)

    verified_on = models.DateField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.college.college_name} - {self.course.course_name}"
