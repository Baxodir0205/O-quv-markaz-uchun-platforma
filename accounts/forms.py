from django import forms
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Parol')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Parolni tasdiqlang')

    full_name = forms.CharField(max_length=150, label='To‘liq ism')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label='Role')

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar bir xil emas")
        return cleaned_data