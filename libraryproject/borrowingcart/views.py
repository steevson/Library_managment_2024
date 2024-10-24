from django.shortcuts import render
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from home.models import Book, CustomUser

from django.contrib import messages
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import BorrowRecord
from staff.models import librarianMemberRequest

from .models import CartList, BorrowRecord, Item
from django.db.models import Sum
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import redirect


def is_librarian(user):
    return user.user_type == 2


def is_member(user):
    return user.user_type == 3


def is_admin(user):
    return user.user_type == 1

#  librarian view



################################################################################ fines ###############


@login_required
@user_passes_test(is_member)
def add_to_cart(request, book_id):
    user = request.user
    book = get_object_or_404(Book, id=book_id)

    # Get or create the cart for the user
    cart, created = CartList.objects.get_or_create(user=user)

    # Check if the item is already in the cart to avoid duplicates
    if not Item.objects.filter(cart=cart, book=book).exists():
        # Explicitly set the book_qty when creating the Item
        Item.objects.create(cart=cart, book=book, book_qty=1)  # Default to 1 book
    else:
        # Optionally, handle case where item is already in the cart (e.g., show a message)
        return redirect('view_cart')

    return redirect('view_cart')  # Redirect to cart after adding the book


@login_required
@user_passes_test(is_member)
def view_cart(request):
    cart = CartList.objects.filter(user=request.user).first()
    items = Item.objects.filter(cart=cart) if cart else []
    return render(request, 'cart/view_cart.html', {'cart': cart, 'items': items})



@login_required
@user_passes_test(is_member)
def borrow_from_cart(request):
    cart = CartList.objects.filter(user=request.user).first()
    items = Item.objects.filter(cart=cart) if cart else []

    if request.method == 'POST':
        for item in items:
            due_date = timezone.now() + timedelta(days=2)
            BorrowRecord.objects.create(
                book=item.book,
                member=request.user,
                status='Pending Approval',
                due_date=due_date  # Set the due date here
            )
            item.delete()  # Remove the item from the cart after borrowing request

        return redirect('borrow_request_success')

    return render(request, 'cart/borrow_from_cart.html', {'items': items})





@login_required
@user_passes_test(is_member)
def remove_from_cart(request, item_id):
    # Get the cart and the item
    cart = CartList.objects.filter(user=request.user).first()
    item = get_object_or_404(Item, id=item_id, cart=cart)

    # Delete the item from the cart
    item.delete()

    messages.success(request, "Item removed from your cart.")
    return redirect('view_cart')



######################### fines ##################

# View for displaying pending fines
@login_required
@user_passes_test(is_member)
def pending_fines(request):
    borrow_records = BorrowRecord.objects.filter(member=request.user, status='Returned')
    total_pending_fines = 0
    overdue_fine_per_day = 10  # Fine rate per day

    for record in borrow_records:
        if record.returned_on and record.returned_on > record.due_date:
            # Fine calculation for already returned books
            if not record.fine:  # Avoid recalculating fines
                overdue_days = (record.returned_on - record.due_date).days
                record.fine = overdue_days * overdue_fine_per_day
                record.save()
        elif not record.returned_on and timezone.now() > record.due_date:
            # Fine calculation for overdue books that are not returned yet
            overdue_days = (timezone.now() - record.due_date).days
            record.fine = overdue_days * overdue_fine_per_day
            record.save()

        total_pending_fines += record.fine

    return render(request, 'fines/pending_fines.html', {
        'borrow_records': borrow_records,
        'total_pending_fines': total_pending_fines,
    })


# View for displaying fine payment details
@login_required
@user_passes_test(is_member)
def fine_payment_view(request):
    user = request.user
    fines = BorrowRecord.objects.filter(member=user, status='Returned', fine__gt=0)

    # Calculate total fine
    total_fine = sum(record.fine for record in fines)

    context = {
        'fines': fines,
        'total_fine': total_fine,
        'user': user,
    }
    return render(request, 'fines/payment.html', context)


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.session.get('razorpay_order_id')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.payment.fetch(payment_id)
        print("Payment details:", payment)  # Debugging line

        if payment['status'] == 'captured':
            print("Payment captured:", payment)  # Debugging line

            # Fetch borrow records with outstanding fines
            borrow_records = BorrowRecord.objects.filter(member=request.user, fine__gt=0)
            print(f"Found {borrow_records.count()} records with fines for user {request.user.id}")  # Debugging line

            # Delete each borrow record after confirming payment
            for record in borrow_records:
                print(f"Deleting record {record.id} with fine {record.fine}")  # Debugging line
                record.delete()  # Delete the borrow record after fine is paid

            # Confirm deletion
            remaining_records = BorrowRecord.objects.filter(member=request.user, fine__gt=0)
            print(f"Remaining records after deletion: {remaining_records.count()}")  # Debugging line

            messages.success(request, "Payment successful! Your fines have been cleared.")
        else:
            messages.error(request, "Payment failed. Please try again.")

    return redirect('pending_fines')


# View to mark a book as returned and calculate fines if overdue
@login_required
@user_passes_test(is_member)
def return_book(request, borrow_record_id):
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id, member=request.user)

    if request.method == 'POST':
        borrow_record.returned_on = timezone.now()  # Set the returned date
        borrow_record.status = 'Returned'  # Mark the book as returned

        # Calculate fine if the book is overdue
        if borrow_record.returned_on > borrow_record.due_date:
            overdue_days = (borrow_record.returned_on - borrow_record.due_date).days
            borrow_record.fine = overdue_days * 4  # Fine of 4 per day
        else:
            borrow_record.fine = 0  # Reset fine if returned on time

        borrow_record.save()

        return redirect('pending_fines')

    return render(request, 'fines/return_book.html', {'borrow_record': borrow_record})
