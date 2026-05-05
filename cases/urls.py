from django.urls import path
from .views import case_list, case_detail, teacher_submission_detail

urlpatterns = [
    path('', case_list, name='case_list'),
    path('submission/<int:pk>/', teacher_submission_detail, name='teacher_submission_detail'),
    path('<slug:slug>/', case_detail, name='case_detail'),
]