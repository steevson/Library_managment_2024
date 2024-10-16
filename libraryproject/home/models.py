from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUserManager(UserManager):
    def _create_user(self, email, password, plain_password=None, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)  # Hash the password for security
        user.plain_password = plain_password  # Store plain password for admin view
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, plain_password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, plain_password, **extra_fields)

    def create_superuser(self, email, password=None, plain_password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, plain_password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "Admin"), (2, "Librarian"), (3, "Member"))

    username = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    plain_password = models.CharField(max_length=128, blank=True, null=True)  # Plain password only viewable by admin
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE, default=3)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    # Add related_name to avoid clashes with AbstractUser
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Librarian(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Member(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class MemberRequest(models.Model):
    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)
    username = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=128)  # Store hashed password
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        user = CustomUser.objects.create_user(username=self.username, email=self.email, password=self.password)
        Member.objects.create(user=user)
        self.approved = True
        self.save()

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
    ]
    img = models.ImageField(upload_to='pictures/', blank=True, null=True)
    name = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='education')
    copies_available = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} [{self.isbn}]"


