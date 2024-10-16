from django.db import models
from django.db import models
from django.utils import timezone
from datetime import timedelta
from home.models import CustomUser, Book

class librarianMemberRequest(models.Model):
    USER_TYPE = (3, "Member")
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE, default=3)
    password = models.CharField(max_length=12, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.PositiveSmallIntegerField(USER_TYPE, default=3)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,limit_choices_to={'user_type': 2})  # Assuming user_type 2 is Librarian
    is_approved = models.BooleanField(default=False)