from home.models import Book


def cate(request):
    books = Book.objects.all()
    book_count = books.count()
    return {'books': books, 'book_count': book_count}
