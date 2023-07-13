from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from .models import UserProfile, Book, BorrowedBook, Feedback
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .forms import BookForm


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
        profile = UserProfile(user=user, student_number=student_number, email=email)
        profile.save()

        # Send email to user
        message = f"Thank you for using our ENOTE website, {username}!"
        send_mail('Welcome to ENOTE', message, 'enote7y@gmail.com', [email])

        login(request, user)  # Log in the user after registration
        return redirect('login')  # Redirect to the login page

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
    feedbacks = Feedback.objects.all()
    books = Book.objects.all()

    username = request.user.username
    context = {
        'username': username,
        'feedbacks': feedbacks,
        'books': books
    }
    return render(request, 'dash.html', context)


@login_required
def borrow_book(request):
    user = request.user
    
    # Check if the user has already borrowed a book
    if BorrowedBook.objects.filter(user=user, is_returned=False).exists():
        messages.error(request, 'You have already borrowed a book. Please return it before borrowing another one.')
        return redirect('dash')

    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        book_id = request.POST.get('book')

        try:
            book = Book.objects.get(id=book_id, is_available=True)
        except Book.DoesNotExist:
            messages.error(request, 'Sorry, the selected book is not available for borrowing. Please choose another book.')
            return redirect('borrow')

        borrowed_book = BorrowedBook(user=user, book=book)

        # Set the return date as three days from the borrowed date
        borrowed_book.return_date = datetime.now() + timedelta(days=3)

        borrowed_book.save()

        # Mark the book as unavailable
        book.is_available = False
        book.save()

        # Send confirmation email to the user
        subject = 'Book Borrowed Successfully'
        message = f"Dear {user.username},\n\nYou have successfully borrowed the book: {book.title}.\n\nPlease return the book by {borrowed_book.return_date.strftime('%Y-%m-%d %H:%M:%S')}.\n\nThank you!"
        from_email = 'enote7y@gmail.com'
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])

        messages.success(request, 'Book borrowed successfully. Confirmation email has been sent.')
        return redirect('count')

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


@login_required
def confirm_return(request, borrowed_book_id):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-admin users to the login page

    borrowed_book = BorrowedBook.objects.get(id=borrowed_book_id)
    borrowed_book.is_returned = True
    borrowed_book.book.is_available = True  # Set the book availability to True
    borrowed_book.book.save()  # Save the book to update the availability
    borrowed_book.save()  # Save the borrowed book

    return redirect('acr')



@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            # Perform any additional processing or validation on the book object if needed
            book.save()

            # Send email to the department
            subject = 'New Book Added'
            message = f'A new book "{book.title}" has been added to the library.'
            from_email = 'enote7y@gmail.com'
            to_email = 'enote7y@gmail.com'
            send_mail(subject, message, from_email, [to_email])

            return redirect('success')
    else:
        form = BookForm()

    return render(request, 'add.html', {'form': form})

def success(request):
    return render(request, 'success.html')


def success(request):
    return render(request, 'success.html')

def count (request):
    return render (request, 'count.html')

from .forms import FeedbackForm

def uf(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = FeedbackForm()
    
    return render(request, 'uf.html', {'form': form})

