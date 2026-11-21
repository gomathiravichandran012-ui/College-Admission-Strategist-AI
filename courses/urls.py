
from django.urls import path
from . import views

urlpatterns = [
    path(
        'recommendations/',
        views.course_recommendation_view,
        name='course_recommendations'
    ),
]
