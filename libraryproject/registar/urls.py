from django.urls import path
from . import views


urlpatterns = [

    # Registration URL
    path('register/', views.register, name='register'),

    # Login URL
    path('login/', views.login_user, name='login'),


    # Logout URL
    path('logout/', views.logout_user, name='logout'),


]
