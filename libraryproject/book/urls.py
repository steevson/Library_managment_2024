from django.urls import path
from .views import (
    book_list,
    add_book,
    edit_book,
    delete_book,
    list_all_book,


)

urlpatterns = [
    path('books/', book_list, name='book_list'),  # List all books
    path('books/add/', add_book, name='add_book'),  # Add a new book
    path('books/edit/<int:book_id>/', edit_book, name='edit_book'),  # Edit book details
    path('books/delete/<int:book_id>/', delete_book, name='delete_book'),  # Delete a book
    path('books/all/', list_all_book, name='list_all_book'),  # List all books in detail

]
