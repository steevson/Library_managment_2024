from django.utils import timezone
from home.models import Book, MemberRequest, CustomUser, Member
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from home.models import CustomUser, Member
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from django.contrib import messages
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from borrowingcart.models import  CartList, BorrowRecord, Item
from staff.models import librarianMemberRequest


from django.db.models import Sum
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import redirect


def is_member(user):
    return user.user_type == 3


@login_required
def member_list(request):
    members = CustomUser.objects.filter(user_type=3)  # user_type 3 indicates Members
    return render(request, 'admindashboard/member_list.html', {'members': members})


@login_required
def add_member(request):
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
            return redirect('add_member')

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('add_member')

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
        return redirect('member_management')

    return render(request, 'admindashboard/add_member.html')


@login_required
def member_profile(request):
    member = get_object_or_404(Member, user=request.user)
    return render(request, 'admindashboard/member_profile.html', {'member': member})


def update_member(request, member_id):
    # Get the CustomUser instance with user_type=3 (indicating a Member)
    member_user = get_object_or_404(CustomUser, pk=member_id, user_type=3)
    # Fetch the related Member profile

    if request.method == 'POST':
        # Update basic member details
        member_user.email = request.POST.get('email')
        member_user.first_name = request.POST.get('first_name')
        member_user.contact_number = request.POST.get('contact_number')

        if 'profile_pic' in request.FILES:
            member_user.profile_pic = request.FILES['profile_pic']

        # Update password if provided
        password = request.POST.get('password')
        if password:
            member_user.set_password(password)  # Ensure the password is hashed

        # Save the updated member user details
        member_user.save()

        messages.success(request, 'Member updated successfully!')
        return redirect('member_management')  # Redirect to member management page

    return render(request, 'admindashboard/update_member.html', {'member_user': member_user})


@login_required
def delete_member(request, member_id):
    member_user = get_object_or_404(CustomUser, pk=member_id, user_type=3)
    member_user.delete()
    messages.success(request, 'Member deleted successfully!')
    return redirect('member_management')


@login_required
def member_profile(request):
    user = get_object_or_404(CustomUser, id=request.user.id)
    context = {
        'user': user
    }
    return render(request, 'admindashboard/member_profile.html', context)


@login_required
@user_passes_test(is_member)
def member_borrow_records(request):
    # Fetch the borrow records for the logged-in member
    borrow_records = BorrowRecord.objects.filter(member=request.user)

    # Loop through each record and calculate the fine
    for record in borrow_records:
        if record.status == 'Returned':  # Only calculate fine if the book is returned
            record.fine = record.calculate_fine()  # This now correctly uses the returned_on attribute

    # Render the records to the member_borrow_records.html template
    return render(request, 'request_temp/member_borrow_records.html', {'borrow_records': borrow_records})


@login_required
@user_passes_test(is_member)
def return_book(request, borrow_record_id):
    # Retrieve the borrow record and ensure it's associated with the logged-in user
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id, member=request.user)

    if request.method == 'POST':
        # Instead of immediately returning the book, set the status to 'Return Requested'
        if borrow_record.status == 'Borrowed':
            borrow_record.status = 'Return Requested'
            borrow_record.save()

        messages.success(request, "Return request has been submitted and is awaiting librarian approval.")

        return redirect('member_borrow_records')

    return render(request, 'request_temp/return_book.html', {'borrow_record': borrow_record})


@login_required
@user_passes_test(is_member)
def request_book_return(request, borrow_record_id):
    borrow_record = get_object_or_404(BorrowRecord, id=borrow_record_id, member=request.user)

    if request.method == 'POST':
        borrow_record.request_return()  # Change status to 'Return Pending Approval'
        messages.success(request, "Your return request has been submitted and is awaiting librarian approval.")
        return redirect('member_borrow_records')

    return render(request, 'request_temp/request_book_return.html', {'borrow_record': borrow_record})


@login_required
@user_passes_test(is_member)
def borrow_request_success(request):
    return render(request, 'request_temp/borrow_request_success.html')
