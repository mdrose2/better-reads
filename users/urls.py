"""
URL patterns for the users app.

This module defines all URL routes for user-related functionality including:
- Registration and authentication
- Profile management
- Password reset
- Email verification
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

# ==============================================================================
# URL PATTERNS
# ==============================================================================
# Note: Order matters - specific patterns come before dynamic ones

urlpatterns = [
    
    # ==========================================================================
    # REGISTRATION & AUTHENTICATION
    # ==========================================================================
    path('register/', 
         views.register, 
         name='register'),
    
    path('login/', 
         auth_views.LoginView.as_view(template_name='users/login.html'), 
         name='login'),
    
    path('logout/', 
         auth_views.LogoutView.as_view(), 
         name='logout'),
    
    # ==========================================================================
    # PROFILE MANAGEMENT
    # ==========================================================================
    # Specific paths first (no parameters)
    path('profile/edit/', 
         views.edit_profile, 
         name='edit-profile'),
    
    path('profile/delete/', 
         views.delete_account, 
         name='delete-account'),
    
    # Dynamic path last (with username parameter)
    path('profile/<str:username>/', 
         views.profile, 
         name='profile'),
    
    # ==========================================================================
    # PASSWORD RESET
    # ==========================================================================
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # ==========================================================================
    # EMAIL VERIFICATION
    # ==========================================================================
    path('verify-email/<uidb64>/<token>/', 
         views.verify_email, 
         name='verify-email'),
    
    path('resend-verification/', 
         views.resend_verification, 
         name='resend-verification'),
]