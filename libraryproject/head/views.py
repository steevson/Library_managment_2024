from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from django.contrib import messages

from django.contrib import messages
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from staff.models import librarianMemberRequest

from borrowingcart.models import CartList, BorrowRecord, Item
from django.db.models import Sum
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import redirect

from home.models import CustomUser


def is_admin(user):
    return user.user_type == 1



@login_required
@user_passes_test(is_admin)  # Assuming 1 is the user_type for Admin
def member_borrow_summary(request):
    # Get all members
    members = CustomUser.objects.filter(user_type=3)  # Assuming 3 is the user_type for Member

    # Initialize an empty list to store member summary data
    member_summary = []

    # Loop through each member to get their borrowing records and fines
    for member in members:
        borrow_records = BorrowRecord.objects.filter(member=member)

        # Calculate total borrowed books and total fines
        total_borrowed = borrow_records.count()
        total_fine = borrow_records.aggregate(Sum('fine'))['fine__sum'] or 0  # Sum of fines, default to 0 if None

        # Append summary for this member
        member_summary.append({
            'member': member,
            'total_borrowed': total_borrowed,
            'total_fine': total_fine,
        })

    # Calculate the total sum of fines across all members
    total_fines_collected = sum(item['total_fine'] for item in member_summary)

    return render(request, 'request_temp/member_borrow_summary.html', {
        'member_summary': member_summary,
        'total_fines_collected': total_fines_collected,
    })


@login_required
@user_passes_test(lambda u: u.user_type == 1)  # Assuming 1 is the user_type for Admin
def approve_or_reject_member_request(request, request_id):
    member_request = get_object_or_404(librarianMemberRequest, id=request_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            if member_request.is_approved:
                messages.info(request, "This member request has already been approved.")
                return redirect('manage_member_requests')

            # Create new member user from request
            user = CustomUser.objects.create_user(
                username=member_request.username,
                first_name=member_request.first_name,
                last_name=member_request.last_name,
                email=member_request.email,
                password='default_password',  # Use a default password or generate one
                user_type=3,  # Assuming 3 is for Member
                address=member_request.address,
                contact_number=member_request.contact_number
            )
            user.save()

            # Mark the request as approved
            member_request.is_approved = True
            member_request.save()

            messages.success(request, "Member approved and account created.")
            return redirect('manage_member_requests')

        elif action == 'reject':
            # Rejecting the member request
            member_request.delete()
            messages.success(request, "Member request has been rejected.")
            return redirect('manage_member_requests')

    return render(request, 'request_temp/approve_member_request.html', {'member_request': member_request})


@login_required
@user_passes_test(lambda u: u.user_type == 1)  # Assuming 1 is the user_type for Admin
def manage_member_requests(request):
    pending_requests = librarianMemberRequest.objects.filter(is_approved=False)
    member_request_count = pending_requests.count()  # Get the count of pending requests

    # You might want to include other relevant data here if needed
    context = {
        'pending_requests': pending_requests,
        'member_request_count': member_request_count,  # Pass the count to the template
    }
    return render(request, 'request_temp/manage_member_requests.html', context)