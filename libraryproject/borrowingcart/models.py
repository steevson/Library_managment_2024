from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

from datetime import timedelta, datetime
from home.models import CustomUser, Book
from django.utils import timezone
import uuid  # for generating unique cart IDs


class CartList(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # Ensures only one cart per user
    cart_id = models.CharField(max_length=250, unique=True, default=uuid.uuid4)  # Unique ID for the cart
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.cart_id)


class Item(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    cart = models.ForeignKey(CartList, on_delete=models.CASCADE)
    book_qty = models.IntegerField(default=1)  # Default value set to 1

    def clean(self):
        if self.book_qty > 2:
            raise ValidationError("You cannot add more than 2 books to your cart.")

    def __str__(self):
        return str(self.book)


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Borrowed', 'Borrowed'),
        ('Returned', 'Returned'),
        ('Return Pending Approval', 'Return Pending Approval'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 3})
    borrowed_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Approval')
    return_approved = models.BooleanField(default=False)  # Track if the return is approved by the librarian
    fine = models.PositiveIntegerField(default=0)

    def return_book(self):
        """Mark the book as returned and update the status."""
        self.return_date = datetime.now()
        self.status = 'Returned'
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk and self.status == 'Borrowed':
            self.due_date = timezone.now() + timedelta(days=2)  # Set due date to 15 days from now
        super().save(*args, **kwargs)

    def approve(self):
        if self.status == 'Pending Approval':
            self.status = 'Borrowed'
            self.book.copies_available -= 1
            self.book.save()
            self.save()

    def return_book(self):
        """Mark the book as returned and update the book's available copies."""
        self.return_date = timezone.now()  # Set the return date to now
        self.status = 'Returned'  # Update status

        # Increment the copies available for the book
        self.book.copies_available += 1
        self.book.save()  # Save changes to the book

        self.save()  # Save changes to the database

    def approve_return(self):
        """Librarian approves the return."""
        if self.status == 'Return Pending Approval':
            self.status = 'Returned'  # Mark as returned
            self.returned_on = timezone.now()  # Update the returned_on date
            self.return_approved = True  # Mark return as approved
            self.book.copies_available += 1  # Increment available copies
            self.book.save()  # Save the changes to the book
            self.save()
    def calculate_fine(self):
        """Calculate the fine if the book is returned late."""
        if self.status == 'Returned' and self.returned_on:  # Changed from return_date to returned_on
            if self.returned_on > self.due_date:  # Using returned_on for comparison
                days_late = (self.returned_on - self.due_date).days
                self.fine = days_late * 4  # Assuming 4 rupees per day
                self.save()  # Save the fine to the database
        return self.fine

