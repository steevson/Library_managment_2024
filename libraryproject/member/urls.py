from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.member_list, name='member_management'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/update/<int:member_id>/', views.update_member, name='update_member'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('member_profile', views.member_profile, name='member_profile'),
    path('return_book/<int:borrow_record_id>/', views.return_book, name='return_book'),
    path('borrow/request-return/<int:borrow_record_id>/', views.request_book_return, name='request_book_return'),
    path('my_borrow_records/', views.member_borrow_records, name='member_borrow_records'),
    path('borrow_request_success/', views.borrow_request_success, name='borrow_request_success'),


]