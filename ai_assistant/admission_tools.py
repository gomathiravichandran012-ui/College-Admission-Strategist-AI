
from colleges.models import CollegeCourse


def search_college_courses(course_name="", state="", max_fee=None):
    """
    Search active colleges offering a course.
    Returns college, course and verified fee information.
    """

    records = CollegeCourse.objects.filter(
        is_active=True,
        college__is_active=True,
        course__is_active=True
    ).select_related("college", "course")

    if course_name:
        records = records.filter(
            course__course_name__icontains=course_name
        )

    if state:
        records = records.filter(
            college__state__icontains=state
        )

    if max_fee is not None:
        records = records.filter(fee_amount__lte=max_fee)

    results = []

    for record in records:
        results.append({
            "college": record.college.college_name,
            "location": record.college.location,
            "state": record.college.state,
            "course": record.course.course_name,
            "fee_amount": str(record.fee_amount),
            "fee_period": record.fee_period,
            "fee_details": record.fee_details,
            "academic_year": record.academic_year,
            "source_url": record.source_url,
            "verified_on": str(record.verified_on or "")
        })

    return results
