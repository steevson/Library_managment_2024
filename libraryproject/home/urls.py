from django.urls import path
from .import views

urlpatterns = [

    path('', views.intex, name='home'),
    path('home', views.home, name='lib-home'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('librarian_dashboard', views.librarian_dashboard, name='librarian_dashboard'),
    path('member_dashboard', views.member_dashboard, name='member_dashboard'),

  ]