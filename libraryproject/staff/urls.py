from django.urls import path
from . import views

urlpatterns = [
    # For librarians
    path('approve_borrow/<int:borrow_record_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('borrow_records/', views.list_borrow_records, name='list_borrow_records'),
    path('borrow/approve-return/<int:borrow_record_id>/', views.approve_return_request, name='approve_return_request'),
    path('request_add_member/', views.request_add_member, name='request_add_member'),
    path('view_member_request_status/', views.view_member_request_status, name='view_member_request_status'),

    path('librarians/', views.librarian_list, name='staff_management'),
    path('librarians/add/', views.add_librarian, name='add_librarian'),
    path('librarians/update/<int:librarian_id>/', views.update_librarian, name='update_librarian'),
    path('librarians/delete/<int:librarian_id>/', views.delete_librarian, name='delete_librarian'),


]