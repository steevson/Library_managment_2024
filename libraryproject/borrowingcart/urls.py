from django.urls import path
from . import views

urlpatterns = [
    # For cart
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('member/view_cart/', views.view_cart, name='view_cart'),
    path('member/borrow_from_cart/', views.borrow_from_cart, name='borrow_from_cart'),
    path('borrowingcartremove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # For fine payment
    path('pending_fines/', views.pending_fines, name='pending_fines'),
    path('fine-payment/', views.fine_payment_view, name='fine_payment'),
    path('member/payment-success/', views.payment_success, name='payment_success'),
]