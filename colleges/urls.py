from django.urls import path
from . import views

urlpatterns = [
    path(
        'recommendations/',
        views.college_recommendation_view,
        name='college_recommendations'
    ),
]