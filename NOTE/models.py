from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.user.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='books/')

    def __str__(self):
        return self.title