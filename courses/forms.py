from django import forms
from .models import Course


class TeacherCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title',
            'short_description',
            'description',
            'thumbnail',
            'level',
            'is_published',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Kurs nomi',
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Qisqa tavsif',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Kurs haqida batafsil yozing',
                'rows': 6,
            }),
            'level': forms.Select(attrs={
                'class': 'form-input',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }