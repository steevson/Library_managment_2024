from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Correct import for messages
from home.models import Book, Member


# Create your views here.
def book_list(request):
    books = Book.objects.all()
    book_count = books.count()  # Get the total count of books
    return render(request, 'library/book_list.html', {'books': books, 'book_count': book_count})


def add_book(request):
    if request.method == 'POST':
        name = request.POST['name']
        isbn = request.POST['isbn']
        author = request.POST['author']
        category = request.POST['category']
        copies_available = request.POST['copies_available']
        img = request.FILES.get('img', None)

        # Create book instance
        book = Book.objects.create(
            name=name,
            isbn=isbn,
            author=author,
            category=category,
            copies_available=copies_available,
            img=img
        )
        messages.success(request, "Book added successfully")
        return redirect('book_list')  # Redirect to the book list view

    return render(request, 'library/add_book.html')


# Edit book details (Admin or Librarian)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.name = request.POST['name']
        book.isbn = request.POST['isbn']
        book.author = request.POST['author']
        book.category = request.POST['category']
        book.copies_available = request.POST['copies_available']

        # Update image if a new one is provided
        if 'img' in request.FILES:
            book.img = request.FILES['img']

        book.save()
        messages.success(request, "Book updated successfully")
        return redirect('book_list')

    return render(request, 'library/edit_book.html', {'book': book})


def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully")
        return redirect('book_list')

    return render(request, 'library/delete_book.html', {'book': book})


def list_all_book(request):
    books = Book.objects.all()
    book_count = books.count()  # Get the total count of books
    return render(request, 'library/list_all_book.html', {'books': books, 'book_count': book_count})




