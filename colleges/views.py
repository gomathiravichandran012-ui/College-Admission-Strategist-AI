from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from students.models import StudentProfile
from .models import College


@login_required
def college_recommendation_view(request):

    student = StudentProfile.objects.filter(
        user=request.user
    ).first()

    recommended_colleges = []

    if student and student.state:

        student_state = "".join(student.state.split()).casefold()

        active_colleges = College.objects.filter(
            is_active=True
        ).order_by('college_name')

        recommended_colleges = [
            college for college in active_colleges
            if "".join(college.state.split()).casefold() == student_state
        ]

    return render(
        request,
        'colleges/recommendations.html',
        {
            'student': student,
            'recommended_colleges': recommended_colleges,
        }
    )
