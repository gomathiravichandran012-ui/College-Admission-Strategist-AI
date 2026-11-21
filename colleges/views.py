
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from students.models import StudentProfile
from .models import CollegeCourse


@login_required
def college_recommendation_view(request):

    student = StudentProfile.objects.filter(
        user=request.user
    ).first()

    recommended_colleges = []

    if student and student.state and student.education_stream:

        student_state = "".join(
            student.state.split()
        ).casefold()

        # Only verified college-course records
        offerings = CollegeCourse.objects.filter(
            is_active=True,
            is_verified=True,
            college__is_active=True,
            college__is_verified=True,
            course__is_active=True,
            course__course_category__iexact=student.education_stream
        ).select_related(
            'college',
            'course'
        ).order_by(
            'college__college_name'
        )

        seen_colleges = set()

        for offering in offerings:

            college = offering.college

            college_state = "".join(
                college.state.split()
            ).casefold()

            if (
                college_state == student_state
                and college.id not in seen_colleges
            ):
                recommended_colleges.append(college)
                seen_colleges.add(college.id)

    return render(
        request,
        'colleges/recommendations.html',
        {
            'student': student,
            'recommended_colleges': recommended_colleges,
        }
    )
