"""
Email utility functions for the users app.

This module handles all email-related functionality including:
- Verification email sending
- Welcome email sending
- Token generation for email links
"""

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import logging

logger = logging.getLogger(__name__)


def send_verification_email(request, user):
    """
    Send an email verification link to a newly registered user.
    
    Generates a unique token and builds a verification URL that the user
    must click to activate their account.
    
    Args:
        request: The HTTP request object (used to build absolute URLs)
        user: The User instance to send verification to
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Generate verification token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build verification link
        verification_url = request.build_absolute_uri(
            reverse('users:verify-email', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Email content
        subject = 'Verify your email for Better Reads'
        message = f"""
Welcome to Better Reads!
        
Please click the link below to verify your email address:
{verification_url}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


def send_welcome_email(user):
    """
    Send a welcome email after successful email verification.
    
    Args:
        user: The User instance that just verified their email
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        subject = 'Welcome to Better Reads!'
        message = f"""
Hi {user.username},
        
Welcome to Better Reads! Your email has been successfully verified.

Start exploring books and sharing your reviews today!

Happy reading,
The Better Reads Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False