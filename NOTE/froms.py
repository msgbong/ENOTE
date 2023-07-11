from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    student_number = forms.CharField(max_length=20)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'student_number', 'email']
