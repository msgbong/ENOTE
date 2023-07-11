from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from .models import UserProfile  
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def index (request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        student_number = request.POST['student_number']
        email = request.POST['email']

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, student_number=student_number)

        # Send email to user
        message = f"Thank you for using our ENOTE website, {username}!"
        send_mail('Welcome to ENOTE', message, 'enote7y@gmail.com', [email])

        login(request, user)  # Log in the user after registration
        return redirect('login')  # Redirect to the homepage

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Correct usage of login function
            return redirect('dash')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def dashboard(request):
    username = request.user.username
    context = {
        'username': username
    }
    return render(request, 'dash.html', context)