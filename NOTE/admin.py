from django.contrib import admin
from .models import UserProfile, Book, BorrowedBook, Feedback

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(BorrowedBook)
admin.site.register(Feedback)
