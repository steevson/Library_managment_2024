import uuid

from django.contrib import auth
from django.core.checks import messages

from django.contrib.auth.decorators import login_required
from home.models import CustomUser, Member

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib import messages


# Registration View
def register(request):
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
            return redirect('register')

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

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
        return redirect('login')

    return render(request, 'register_login/register.html')


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using the email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            # Debugging to check user_type
            print(f"User type: {user.user_type}")

            # Redirect based on user type
            if user.user_type == 1:
                return redirect('admin_dashboard')
            elif user.user_type == 2:
                return redirect('librarian_dashboard')
            elif user.user_type == 3:
                return redirect('member_dashboard')
            else:
                messages.error(request, "Invalid user type")
                return redirect('login')

        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'register_login/login.html')


# Logout View
def logout_user(request):
    logout(request)
    return redirect('home')



