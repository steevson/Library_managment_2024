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
            due_date = timezone.now() + timedelta(days=15)  # Set due date to 15 days from now
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




@login_required
@user_passes_test(is_member)  # Assuming 3 is the user_type for Member
def pending_fines(request):
    # Get the borrow records of the logged-in member
    borrow_records = BorrowRecord.objects.filter(member=request.user, fine__gt=0)

    total_pending_fines = sum(record.fine for record in borrow_records)

    return render(request, 'fines/pending_fines.html', {
        'borrow_records': borrow_records,
        'total_pending_fines': total_pending_fines,
    })


@login_required
@user_passes_test(is_member)  # Assuming 3 is the user_type for Member
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
        # Get data from the request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.session.get('razorpay_order_id')

        # Verify payment (optional but recommended)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.payment.fetch(payment_id)

        if payment['status'] == 'captured':
            # Payment successful, update the fine records
            borrow_records = BorrowRecord.objects.filter(member=request.user, fine__gt=0)
            for record in borrow_records:
                record.fine = 0  # Reset fine after payment
                record.save()
            messages.success(request, "Payment successful! Your fines have been cleared.")
        else:
            messages.error(request, "Payment failed. Please try again.")

    return redirect('pending_fines')


@login_required
@user_passes_test(is_member)
def pending_fines(request):
    # Logic to fetch pending fines for the member, if any.

    return render(request, 'fines/pending_fines.html')
# Create your views here.


