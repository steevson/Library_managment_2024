from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Book, MemberRequest, CustomUser, Member
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import CustomUser, MemberRequest, Member, Librarian
from django.contrib.auth.hashers import make_password
from datetime import timedelta


def intex(request):
    return render(request, 'intex.html')


# Home page or dashboard
def home(request):
    books = Book.objects.all()
    return render(request, 'library/home.html', {'books': books})


def admin_dashboard(request):
    return render(request, "dashboards/admin_dashboard.html")


def member_dashboard(request):
    return render(request, 'dashboards/member_dashboard.html')


def librarian_dashboard(request):
    return render(request, "dashboards/librarian_dashboard.html")


