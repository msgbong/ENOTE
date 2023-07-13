from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['student_number', 'email']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['student_number'].label = 'Student Number'


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'is_available', 'image')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # Add any custom validation or cleaning logic for the title field if needed
        return title

    def clean_author(self):
        author = self.cleaned_data.get('author')
        # Add any custom validation or cleaning logic for the author field if needed
        return author
    

from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('name', 'email', 'message')