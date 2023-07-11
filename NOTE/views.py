from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from .models import UserProfile, Book, BorrowedBook
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta


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

@login_required
def borrow_book(request):
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        book_id = request.POST.get('book')

        try:
            book = Book.objects.get(id=book_id, is_available=True)
        except Book.DoesNotExist:
            messages.error(request, 'Sorry, the selected book is not available for borrowing. Please choose another book.')
            return redirect('bborrow')

        borrowed_book = BorrowedBook(user=request.user, book=book)

        # Set the return date as three days from the borrowed date
        borrowed_book.return_date = datetime.now() + timedelta(days=3)

        borrowed_book.save()

        # Mark the book as unavailable
        book.is_available = False
        book.save()

        # Send confirmation email
        send_mail(
            'Book Borrowed',
            'You have successfully borrowed the book.',
            'enote7y@gmail.com',
            [request.user.email],
            fail_silently=False,
        )

        messages.success(request, 'Book borrowed successfully. Confirmation email has been sent.')
        return redirect('dash')

    # Fetch available books to populate the dropdown
    available_books = Book.objects.filter(is_available=True)
    context = {'books': available_books}
    return render(request, 'bborrow.html', context)

def acr(request):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-admin users to login page

    borrowed_books = BorrowedBook.objects.filter(is_returned=False)
    context = {'borrowed_books': borrowed_books}
    return render(request, 'acr.html', context)


def confirm_return(request, borrowed_book_id):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-admin users to login page

    borrowed_book = BorrowedBook.objects.get(id=borrowed_book_id)
    borrowed_book.is_returned = True
    borrowed_book.save()

    return redirect('acr') 

@login_required
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        is_available = request.POST.get('is_available')

        book = Book(title=title, author=author, is_available=is_available)
        book.save()

        return redirect('dash')  # Redirect to the book list page after adding the book

    return render(request, 'add.html')