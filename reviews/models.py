"""
Review model definitions for the reviews app.

Handles user reviews of books, including rating system with half-star support
and automatic slug generation for SEO-friendly URLs.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from books.models import Book


class Review(models.Model):
    """
    Represents a user's review of a specific book.
    
    Each user can only write one review per book (enforced by unique_together).
    Reviews include a rating (0-5 stars with half-star increments), a title,
    and detailed content. URLs use automatically generated slugs for SEO.
    
    Relationships:
        - user: The User who wrote the review
        - book: The Book being reviewed
    """
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="User who wrote this review"
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Book being reviewed"
    )
    
    # =========================================================================
    # REVIEW CONTENT
    # =========================================================================
    
    rating = models.DecimalField(
        max_digits=2,  # Allows values like 5.0, 4.5, 3.0
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
        """String representation showing user, rating, and book."""
        return f"{self.user.username}'s {self.rating}-star review of {self.book.title}"
    
    # =========================================================================
    # DISPLAY METHODS
    # =========================================================================
    
    def get_star_rating(self):
        """
        Convert numeric rating to visual star representation.
        
        Returns a string with star symbols:
        - ★ for full stars
        - ½ for half stars
        - ☆ for empty stars
        
        Example: 4.5 stars → "★★★★½"
        """
        full_stars = int(self.rating)  # Integer part (e.g., 4 from 4.5)
        half_star = (self.rating - full_stars) >= 0.5  # True if half star needed
        
        # Build the star string
        stars = '★' * full_stars
        if half_star:
            stars += '½'  # Half star symbol
        stars += '☆' * (5 - full_stars - (1 if half_star else 0))
        
        return stars
    
    def get_star_percentage(self):
        """
        Convert rating to percentage for CSS progress bars.
        
        Returns a float between 0 and 100.
        Example: 4.5 stars → 90%
        """
        return (self.rating / 5) * 100
    
    def is_edited(self):
        """
        Check if the review has been edited after creation.
        
        Returns:
            bool: True if updated_at differs from created_at
        """
        return self.updated_at > self.created_at
    
    # =========================================================================
    # SLUG GENERATION
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate URL-friendly slug.
        
        Slug format: [username]-review-of-[book-title]-[timestamp]
        Example: johndoe-review-of-the-great-gatsby-20250301123456
        
        Ensures uniqueness by appending counter if timestamp collision occurs.
        """
        if not self.slug:
            # Create base slug from username and book title
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            base_slug = slugify(
                f"{self.user.username}-review-of-{self.book.title}"
            )[:70]  # Leave room for timestamp and counter
            self.slug = f"{base_slug}-{timestamp}"
            
            # Ensure uniqueness (timestamp should be sufficient, but just in case)
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
    
    # =========================================================================
    # PROPERTIES
    # =========================================================================
    
    @property
    def is_recent(self):
        """Check if review was created in the last 7 days."""
        return (timezone.now() - self.created_at).days < 7
    
    @property
    def word_count(self):
        """Return the number of words in the review content."""
        return len(self.content.split())