from django.contrib.auth.decorators import login_required
from django.utils import timezone
from home.models import (Book, MemberRequest, CustomUser, Member)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from home.models import CustomUser, Librarian
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import librarianMemberRequest
from django.contrib import messages
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from borrowingcart.models import CartList, BorrowRecord, Item
from staff.models import librarianMemberRequest

from django.db.models import Sum
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import redirect


def is_librarian(user):
    return user.user_type == 2


def librarian_list(request):
    librarians = CustomUser.objects.filter(user_type=2)  # user_type 2 indicates Librarians
    return render(request, 'admindashboard/librarian_list.html', {'librarians': librarians})


def add_librarian(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_type = request.POST['user_type']
        username = request.POST.get('username')  # Add this line to get the username
        address = request.POST.get('address', '')
        contact_number = request.POST.get('contact_number', '')

        # Password confirmation check
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('add_librarian')

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('add_librarian')

        # Create user
        user = CustomUser.objects.create_user(
            username=username,  # Pass the username to create_user
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            user_type=user_type,
            address=address,
            contact_number=contact_number
        )

        user.save()
        messages.success(request, "Account created successfully")
        return redirect('staff_management')

    return render(request, 'admindashboard/add_librarian.html')


def update_librarian(request, librarian_id):
    librarian_user = get_object_or_404(CustomUser, pk=librarian_id, user_type=2)

    # librarian = get_object_or_404(Librarian, user=librarian_user)

    if request.method == 'POST':
        librarian_user.email = request.POST.get('email')
        librarian_user.first_name = request.POST.get('name')
        librarian_user.contact_number = request.POST.get(
            'contact_number')  # Using `contact_number` instead of `contact_details`

        # Update profile image if a new one is provided
        if 'profile_pic' in request.FILES:
            librarian_user.profile_pic = request.FILES['profile_pic']

        # Update password if provided
        password = request.POST.get('password')
        if password:
            librarian_user.set_password(password)  # Ensure the password is hashed

        librarian_user.save()

        messages.success(request, 'Librarian updated successfully!')
        return redirect('staff_management')

    return render(request, 'admindashboard/update_librarian.html',
                  {'librarian_user': librarian_user})


def delete_librarian(request, librarian_id):
    librarian_user = get_object_or_404(CustomUser, pk=librarian_id, user_type=2)
    librarian_user.delete()
    messages.success(request, 'Librarian deleted successfully!')
    return redirect('staff_management')


@login_required
@user_passes_test(is_librarian)
def approve_return_request(request, borrow_record_id):
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)

    if request.method == 'POST':
        borrow_record.return_book()  # This will update the book's copies_available

        messages.success(request, "Book return approved successfully.")
        return redirect('list_borrow_records')  # Redirect to the list after approval

    return render(request, 'request_temp/approve_return_request.html', {'borrow_record': borrow_record})

@login_required
@user_passes_test(is_librarian)  # Create this test function based on user roles
def list_borrow_records(request):
    borrow_records = BorrowRecord.objects.all()  # Get all borrow records for librarians
    return render(request, 'request_temp/list_borrow_records.html', {'borrow_records': borrow_records})


@login_required
@user_passes_test(is_librarian)
def approve_borrow_request(request, borrow_record_id):
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id)

    if request.method == 'POST':
        borrow_record.approve()  # Call the approve method
        return redirect('list_borrow_records')  # Redirect to the list of borrow records after approval

    return render(request, 'request_temp/approve_borrow_request.html', {'borrow_record': borrow_record})


@login_required
@user_passes_test(lambda u: u.user_type == 2)  # Assuming 2 is the user_type for Librarians
def request_add_member(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')

        # Create a new member request
        new_request = librarianMemberRequest.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            contact_number=contact_number,
            requested_by=request.user
        )
        new_request.save()

        messages.success(request, "Member request submitted successfully.")
        return redirect('view_member_request_status')  # Redirect to librarian dashboard or another page

    return render(request, 'request_temp/request_add_member.html')


@login_required
@user_passes_test(lambda u: u.user_type == 2)  # Assuming 2 is the user_type for Librarians
def view_member_request_status(request):
    # Get all requests submitted by the logged-in librarian
    member_requests = librarianMemberRequest.objects.filter(requested_by=request.user)
    return render(request, 'request_temp/view_member_request_status.html', {'member_requests': member_requests})
