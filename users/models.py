"""
User model definitions for the users app.

This module defines the custom User model that extends Django's AbstractUser
to add profile fields and email verification capabilities.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Adds:
    - Profile bio
    - Profile picture upload
    - Email verification tracking
    - Last active timestamp
    
    This model is referenced via AUTH_USER_MODEL in settings.
    """
    
    # =========================================================================
    # PROFILE FIELDS
    # =========================================================================
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell us a little about yourself (max 500 characters)"
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Upload a profile picture (JPG, PNG, GIF accepted)"
    )
    
    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================
    
    email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user has verified their email address"
    )
    
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Token used for email verification (expires after use)"
    )
    
    # =========================================================================
    # ACCOUNT TIMESTAMPS
    # =========================================================================
    
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user registered"
    )
    
    last_active = models.DateTimeField(
        default=timezone.now,
        help_text="Last time the user was active on the site"
    )
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['email_verified']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        """Return email or username for string representation."""
        return self.email or self.username
    
    def get_full_name(self):
        """
        Return the user's full name if available, otherwise username.
        
        Returns:
            str: Full name or username.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_profile_picture_url(self):
        """
        Return profile picture URL or default placeholder.
        
        Returns:
            str: URL of profile picture or None.
        """
        if self.profile_picture:
            return self.profile_picture.url
        return None
    
    def update_last_active(self):
        """Update the last_active timestamp to now."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])