from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ==================================
    # TEACHER PANEL
    # ==================================
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),

    # Groups
    path('teacher/groups/', views.teacher_groups, name='teacher_groups'),
    path('teacher/groups/<int:group_id>/', views.teacher_group_detail, name='teacher_group_detail'),

    # Students
    path('teacher/students/', views.teacher_students, name='teacher_students'),

    # Lessons
    path('teacher/lessons/', views.teacher_lessons, name='teacher_lessons'),
    path('teacher/lessons/group/<int:group_id>/', views.teacher_group_lessons, name='teacher_group_lessons'),
    path('teacher/lessons/create/', views.create_lesson, name='create_lesson'),
    path('teacher/lessons/delete/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),

    # Assignments
    path('teacher/assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('teacher/assignments/create/', views.create_assignment, name='create_assignment'),
    path('teacher/assignments/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('teacher/submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),

    # Tests
    path('teacher/tests/', views.teacher_tests, name='teacher_tests'),
    path('teacher/tests/create/', views.create_test, name='create_test'),
    path('teacher/tests/<int:test_id>/results/', views.test_results, name='test_results'),
    path('teacher/tests/<int:test_id>/delete/', views.delete_test, name='delete_test'),

    # Case Study
    path('teacher/cases/', views.teacher_cases, name='teacher_cases'),
    path('teacher/cases/create/', views.create_case, name='create_case'),
    path('teacher/cases/<int:case_id>/submissions/', views.case_submissions, name='case_submissions'),
    path('teacher/case-submissions/<int:submission_id>/grade/', views.grade_case_submission, name='grade_case_submission'),

    # ==================================
    # STUDENT PANEL
    # ==================================
    path('student/', views.student_dashboard, name='student_dashboard'),

    path('student/lessons/', views.student_lessons, name='student_lessons'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/tests/', views.student_tests, name='student_tests'),
    path('student/cases/', views.student_cases, name='student_cases'),

    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/test/<int:test_id>/solve/', views.solve_test, name='solve_test'),
    path('student/case/<int:case_id>/solve/', views.solve_case, name='solve_case'),
]