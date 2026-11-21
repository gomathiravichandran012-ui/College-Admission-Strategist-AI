
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from students.models import StudentProfile
from .models import Course


@login_required
def course_recommendation_view(request):

    student = StudentProfile.objects.get(user=request.user)

    recommended_courses = []

    if student.education_stream and student.percentage is not None:

        recommended_courses = Course.objects.filter(
            course_category__iexact=student.education_stream,
            minimum_percentage__lte=student.percentage,
            is_active=True
        ).order_by('course_name')

    return render(
        request,
        'courses/recommendations.html',
        {
            'student': student,
            'recommended_courses': recommended_courses,
        }
    )

