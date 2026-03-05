from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Review(models.Model):
    """
    Represents a user's review of a specific book.
    
    Features:
    - Rating system with half-star support (0-5 in 0.5 increments)
    - Automatic slug generation for SEO-friendly URLs
    - Privacy-preserving user reference (SET_NULL on user deletion)
    """
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Changed from CASCADE to preserve reviews
        null=True,
        blank=True,
        related_name='reviews',
        help_text="User who wrote this review (null if user deleted)"
    )
    
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Book being reviewed"
    )
    
    # =========================================================================
    # REVIEW CONTENT
    # =========================================================================
    
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating from 0-5 stars (half-star increments allowed)"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Brief summary of the review"
    )
    
    content = models.TextField(
        help_text="Detailed review content"
    )
    
    # =========================================================================
    # URL SLUG
    # =========================================================================
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the review (auto-generated)"
    )
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this review was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this review was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'book']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'book']),
            models.Index(fields=['slug']),
        ]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
    
    def __str__(self):
        """String representation showing author (anonymized if needed) and book."""
        author = self.display_author
        return f"{author}'s {self.rating}-star review of {self.book.title}"
    
    # =========================================================================
    # DISPLAY PROPERTIES
    # =========================================================================
    
    @property
    def display_author(self):
        """
        Return appropriate author display name.
        
        Handles:
        - Deleted/anonymized users
        - Regular active users
        - Null users (if user was hard-deleted)
        """
        if self.user is None:
            return "deleted_user"
        if getattr(self.user, 'is_anonymized', False):
            return "deleted_user"
        return self.user.username
    
    @property
    def is_visible(self):
        """
        Determine if review should be publicly visible.
        
        Reviews are always visible, even from deleted users,
        to preserve community content.
        """
        return True
    
    def get_star_rating(self):
        """
        Convert numeric rating to visual star representation.
        
        Returns a string with star symbols:
        - ★ for full stars
        - ½ for half stars
        - ☆ for empty stars
        
        Example: 4.5 stars → "★★★★½"
        """
        full_stars = int(self.rating)
        half_star = (self.rating - full_stars) >= 0.5
        
        stars = '★' * full_stars
        if half_star:
            stars += '½'
        stars += '☆' * (5 - full_stars - (1 if half_star else 0))
        
        return stars
    
    def get_star_percentage(self):
        """Convert rating to percentage for CSS progress bars."""
        return (self.rating / 5) * 100
    
    def is_edited(self):
        """
        Check if the review has been edited after creation.
        
        Adds a small buffer (1 second) to prevent false positives on initial save.
        """
        if not self.pk:
            return False
        
        time_diff = self.updated_at - self.created_at
        return time_diff.total_seconds() > 1
    
    @property
    def word_count(self):
        """Return the number of words in the review content."""
        if not self.content:
            return 0
        return len(self.content.split())
    
    @property
    def is_recent(self):
        """Check if review was created in the last 7 days."""
        return (timezone.now() - self.created_at).days < 7
    
    # =========================================================================
    # SLUG GENERATION
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate URL-friendly slug.
        
        Slug format: [username]-review-of-[book-title]-[timestamp]
        Example: johndoe-review-of-the-great-gatsby-20250301123456
        
        For anonymized users, uses 'deleted_user' prefix.
        """
        if not self.slug:
            # Use display_author for consistent naming
            author = self.display_author.replace(' ', '-').lower()
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            base_slug = slugify(
                f"{author}-review-of-{self.book.title}"
            )[:70]
            self.slug = f"{base_slug}-{timestamp}"
            
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Review.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    # =========================================================================
    # URL METHODS
    # =========================================================================
    
    def get_absolute_url(self):
        """Return the canonical URL for this review's detail page."""
        return reverse('reviews:detail', kwargs={'slug': self.slug})