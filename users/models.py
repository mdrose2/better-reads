from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Features:
    - Profile bio and picture
    - Email verification tracking
    - Account anonymization for privacy-preserving deletion
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
    # ACCOUNT STATUS
    # =========================================================================
    
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user registered"
    )
    
    last_active = models.DateTimeField(
        default=timezone.now,
        help_text="Last time the user was active on the site"
    )
    
    is_anonymized = models.BooleanField(
        default=False,
        help_text="Whether this account has been anonymized after deletion"
    )
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['email_verified']),
            models.Index(fields=['is_anonymized']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        """Return email or username for string representation."""
        if self.is_anonymized:
            return "deleted_user"
        return self.email or self.username
    
    def get_full_name(self):
        """
        Return the user's full name if available, otherwise username.
        """
        if self.is_anonymized:
            return "Deleted User"
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_profile_picture_url(self):
        """
        Return profile picture URL or default placeholder.
        """
        if self.profile_picture and not self.is_anonymized:
            return self.profile_picture.url
        return None
    
    def update_last_active(self):
        """Update the last_active timestamp to now."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
    
    def anonymize(self):
        """
        Permanently anonymize user account for privacy-preserving deletion.
        
        This replaces all personal identifying information with placeholders
        while preserving the account for database integrity. The user can no
        longer log in, but their contributed content (reviews, books) remains
        with anonymous attribution.
        """
        # Store original values for logging (optional)
        original_username = self.username
        original_email = self.email
        
        # Anonymize identifying fields
        self.username = f"deleted_user_{self.id}"
        self.email = f"deleted_{self.id}@example.com"
        self.first_name = ''
        self.last_name = ''
        self.bio = ''
        self.profile_picture = None
        
        # Disable account
        self.is_active = False
        self.is_anonymized = True
        self.email_verified = False
        self.email_verification_token = None
        
        self.save()
        
        # Log the anonymization (optional)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"User {original_username} (ID: {self.id}) anonymized")
        
        return True
    
    def delete_account(self):
        """
        Public method for account deletion with privacy preservation.
        This should be called instead of regular delete().
        """
        return self.anonymize()