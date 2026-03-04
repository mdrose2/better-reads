"""
View functions for the users app.

This module handles all user-related views including:
- Registration and authentication
- Profile viewing and editing
- Account deletion
- Email verification
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm
from reviews.models import Review
from .utils import send_verification_email, send_welcome_email


# ==============================================================================
# REGISTRATION & AUTHENTICATION
# ==============================================================================

def register(request):
    """
    Handle new user registration.
    
    Creates a new user account with email_verified=False.
    In development, auto-verifies for convenience.
    
    Template: users/register.html
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Development auto-verification (remove in production)
            user.email_verified = True
            user.save()
            
            # Uncomment for production email verification
            # send_verification_email(request, user)
            
            messages.success(
                request,
                'Account created successfully! You can now log in.'
            )
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


# ==============================================================================
# EMAIL VERIFICATION
# ==============================================================================

def verify_email(request, uidb64, token):
    """
    Verify a user's email address using token from verification email.
    
    Args:
        uidb64: URL-safe base64 encoded user ID
        token: Verification token
    
    Returns:
        Redirect to login on success, home on failure
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        
        # Send welcome email
        send_welcome_email(user)
        
        messages.success(request, 'Email verified! You can now log in.')
        return redirect('users:login')
    else:
        messages.error(request, 'Verification link is invalid or expired.')
        return redirect('pages:home')


@login_required
def resend_verification(request):
    """
    Resend verification email to the current user.
    
    Only works if email is not already verified.
    """
    if request.user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('users:profile', username=request.user.username)
    
    send_verification_email(request, request.user)
    messages.success(request, 'Verification email sent!')
    return redirect('users:profile', username=request.user.username)


# ==============================================================================
# PROFILE VIEWS
# ==============================================================================

def profile(request, username):
    """
    Display a public user profile page.
    
    Shows user information and all their reviews with stats.
    
    Template: users/profile.html
    Context:
        - profile_user: The user being viewed
        - reviews: All reviews by this user
        - review_count: Total number of reviews
        - avg_rating: Average rating of all reviews
    """
    user = get_object_or_404(User, username=username)
    user_reviews = Review.objects.filter(
        user=user
    ).select_related('book').order_by('-created_at')
    
    # Calculate average rating
    avg_rating = user_reviews.aggregate(avg=Avg('rating'))['avg']
    
    context = {
        'profile_user': user,
        'reviews': user_reviews,
        'review_count': user_reviews.count(),
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """
    Allow users to edit their own profile information.
    
    Handles:
    - Username changes (with uniqueness validation)
    - Personal information updates
    - Bio edits
    - Profile picture uploads
    
    Template: users/edit_profile.html
    """
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


# ==============================================================================
# ACCOUNT MANAGEMENT
# ==============================================================================

@login_required
def delete_account(request):
    """
    Allow users to permanently delete their account.
    
    Shows confirmation page before deletion.
    All associated reviews will be deleted via CASCADE.
    
    Template: users/delete_account.html
    """
    if request.method == 'POST':
        user = request.user
        # Log the user out
        logout(request)
        # Delete the account
        user.delete()
        messages.success(
            request,
            'Your account has been permanently deleted.'
        )
        return redirect('pages:home')
    
    return render(request, 'users/delete_account.html')