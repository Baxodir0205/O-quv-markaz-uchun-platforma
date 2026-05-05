from django.urls import path
from .views import (
    course_list,
    course_detail,
    enroll_course,
    lesson_detail,
    complete_lesson,
    teacher_course_create,
)

urlpatterns = [
    path('', course_list, name='course_list'),
    path('create/', teacher_course_create, name='teacher_course_create'),
    path('lesson/<int:pk>/', lesson_detail, name='lesson_detail'),
    path('lesson/<int:pk>/complete/', complete_lesson, name='complete_lesson'),
    path('<slug:slug>/enroll/', enroll_course, name='enroll_course'),
    path('<slug:slug>/', course_detail, name='course_detail'),
]