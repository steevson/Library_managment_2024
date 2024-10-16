from django.urls import path
from . import views

urlpatterns = [
    # For admin

    path('approve_or_reject_member_request/<int:request_id>/', views.approve_or_reject_member_request,
         name='approve_or_reject_member_request'),
    path('admin/member-borrow-summary/', views.member_borrow_summary, name='member_borrow_summary'),
    path('manage_member_requests/', views.manage_member_requests, name='manage_member_requests'),
]