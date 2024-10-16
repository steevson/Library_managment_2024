# Generated by Django 5.1.2 on 2024-10-14 22:33

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BorrowRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_on', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('returned_on', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending Approval', 'Pending Approval'), ('Borrowed', 'Borrowed'), ('Returned', 'Returned'), ('Return Pending Approval', 'Return Pending Approval')], default='Pending Approval', max_length=30)),
                ('return_approved', models.BooleanField(default=False)),
                ('fine', models.PositiveIntegerField(default=0)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.book')),
                ('member', models.ForeignKey(limit_choices_to={'user_type': 3}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(default=uuid.uuid4, max_length=250, unique=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_qty', models.IntegerField(default=1)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.book')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='borrowingcart.cartlist')),
            ],
        ),
    ]
