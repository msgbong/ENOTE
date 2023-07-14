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
        messages.error(
            request,
            "You have already borrowed a book. Please return it before borrowing another one.",
        )
        return redirect("bret")

    if request.method == "POST":
        student_number = request.POST.get("student_number")
        email = request.POST.get("email")
        book_id = request.POST.get("book")

        try:
            book = Book.objects.get(id=book_id, is_available=True)
        except Book.DoesNotExist:
            messages.error(
                request,
                "Sorry, the selected book is not available for borrowing. Please choose another book.",
            )
            return redirect("borrow")

        borrowed_book = BorrowedBook(user=user, book=book)

        # Set the return date as three days from the borrowed date
        borrowed_book.return_date = datetime.now() + timedelta(days=3)
        
        # Assign the email to the BorrowedBook instance
        borrowed_book.email = email

        borrowed_book.save()

        # Mark the book as unavailable
        book.is_available = False
        book.save()

        # Send confirmation email to the provided email address
        subject = "Book Borrowed Successfully"
        message = f"Dear {user.username},\n\nYou have successfully borrowed the book: {book.title}.\n\nPlease return the book by {borrowed_book.return_date.strftime('%Y-%m-%d %H:%M:%S')}.\n\nThank you!"
        from_email = "enote7y@gmail.com"  # Customize the sender email
        to_email = email
        try:
            send_mail(subject, message, from_email, [to_email])
            messages.success(
                request, "Book borrowed successfully. Confirmation email has been sent."
            )
        except Exception as e:
            messages.error(
                request,
                "Book borrowed successfully, but failed to send the confirmation email.",
            )

        return redirect("count")

    # Fetch available books to populate the dropdown
    available_books = Book.objects.filter(is_available=True)
    context = {"books": available_books}
    return render(request, "bborrow.html", context)

def acr(request):
    if not request.user.is_staff:
        return redirect('login')  # Redirect non-admin users to login page

    borrowed_books = BorrowedBook.objects.filter(is_returned=False)
    context = {'borrowed_books': borrowed_books}
    return render(request, 'acr.html', context)

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



def count(request):
    user = request.user

    # Get the countdown date from the user's session storage
    count_down_date_str = request.session.get('count_down_date')

    # If the countdown date is not set, calculate and set it
    if not count_down_date_str:
        count_down_date = datetime.now() + timedelta(days=3)
        count_down_date_str = count_down_date.isoformat()
        request.session['count_down_date'] = count_down_date_str

    # Convert the countdown date string back to a datetime object
    count_down_date = datetime.fromisoformat(count_down_date_str)

    # Calculate the remaining time
    current_time = datetime.now()
    time_difference = count_down_date - current_time

    # Check if the countdown has elapsed
    if time_difference.total_seconds() <= 0:
        # Send email notification
        subject = "Countdown Time Elapsed"
        message = f"Dear {user.username},\n\nThe countdown time has elapsed. You are fined 10,000/= for each day of delay.\n\nPlease make the payment promptly.\n\nThank you!"
        from_email = "your-email@example.com"  # Customize the sender email
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])

        # Calculate the number of days of delay
        delay_days = abs(time_difference.days)

        # Calculate the fine amount
        fine_amount = delay_days * 10000

        # Update user's account balance
        user.account_balance -= fine_amount
        user.save()

        # Log the fine
        Fine.objects.create(user=user, amount=fine_amount, delay_days=delay_days)

    # Extract the days, hours, minutes, and seconds
    days = time_difference.days
    hours = time_difference.seconds // 3600
    minutes = (time_difference.seconds % 3600) // 60
    seconds = time_difference.seconds % 60

    context = {
        'user': user,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'count_down_date': count_down_date_str
    }

    return render(request, 'count.html', context)


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

def bret (request):
    return render(request, 'bret.html')