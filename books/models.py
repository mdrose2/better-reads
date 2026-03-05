"""
Book model definitions for the books app.
Handles storage and retrieval of book information from both Google Books API
and user-submitted indie books.
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
import random
import string


class Book(models.Model):
    """
    Represents a book in the library.
    
    Books can come from two sources:
    1. Google Books API (has google_books_id, is_indie=False)
    2. User submissions (is_indie=True, added_by tracks contributor)
    
    The model stores comprehensive book metadata including cover images,
    publication details, and categorical information.
    """
    
    # =========================================================================
    # BASIC BOOK INFORMATION
    # =========================================================================
    
    title = models.CharField(
        max_length=500,
        help_text="Full title of the book"
    )
    
    subtitle = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Book subtitle, if any"
    )
    
    authors = models.JSONField(
        default=list,
        help_text="List of author names"
    )
    
    # =========================================================================
    # IDENTIFIERS
    # =========================================================================
    
    isbn_13 = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(13)],
        help_text="13-digit International Standard Book Number"
    )
    
    isbn_10 = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(10)],
        help_text="10-digit International Standard Book Number"
    )
    
    google_books_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique identifier from Google Books API"
    )
    
    # =========================================================================
    # PUBLICATION DETAILS
    # =========================================================================
    
    publisher = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Book publisher"
    )
    
    published_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of publication"
    )
    
    page_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total number of pages"
    )
    
    # =========================================================================
    # DESCRIPTIVE CONTENT
    # =========================================================================
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Book description or synopsis"
    )
    
    categories = models.JSONField(
        default=list,
        help_text="List of genres/categories"
    )
    
    # =========================================================================
    # COVER IMAGES
    # =========================================================================
    
    cover_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to high-resolution cover image"
    )
    
    thumbnail_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to small thumbnail image"
    )
    
    # =========================================================================
    # BOOK SOURCE TRACKING
    # =========================================================================
    
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books_added',
        help_text="User who added this book (null for API-imported books)"
    )
    
    is_indie = models.BooleanField(
        default=False,
        help_text="True for user-submitted indie books, False for API imports"
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this book was added to the library"
    )
    
    # =========================================================================
    # URL SLUG
    # =========================================================================
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title (auto-generated)"
    )
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['google_books_id']),
            models.Index(fields=['is_indie']),
            models.Index(fields=['slug']),
        ]
        verbose_name = "Book"
        verbose_name_plural = "Books"
    
    def __str__(self):
        """String representation of the book."""
        return self.title
    
    # =========================================================================
    # SLUG GENERATION
    # =========================================================================
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate URL-friendly slug from title.
        
        If no slug exists, creates one by:
        1. Slugifying the title (lowercase, hyphenated)
        2. Truncating to 50 characters
        3. Ensuring uniqueness by appending random string if needed
        """
        if not self.slug:
            # Create base slug from title
            base_slug = slugify(self.title)[:50]
            slug = base_slug
            
            # Ensure slug uniqueness
            counter = 1
            while Book.objects.filter(slug=slug).exists():
                # Add random string for uniqueness
                random_string = ''.join(
                    random.choices(string.ascii_lowercase + string.digits, k=4)
                )
                slug = f"{base_slug}-{random_string}"
                counter += 1
                
                # Safety check to prevent infinite loop
                if counter > 10:
                    slug = f"{base_slug}-{random_string}"
                    break
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    # =========================================================================
    # URL METHODS
    # =========================================================================
    
    def get_absolute_url(self):
        """Return the canonical URL for this book's detail page."""
        return reverse('books:detail', kwargs={'slug': self.slug})
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def get_authors_list(self):
        """
        Return authors as a list.
        
        Handles cases where authors might be stored as JSON string or list.
        """
        if isinstance(self.authors, list):
            return self.authors
        elif isinstance(self.authors, str):
            return [self.authors]
        return []
    
    def get_categories_list(self):
        """Return categories as a list."""
        if isinstance(self.categories, list):
            return self.categories
        return []
    
    def average_rating(self):
        """
        Calculate the average rating for this book from all reviews.
        Returns None if no reviews exist or if an error occurs.
        """
        try:
            # Safely get all reviews
            reviews = self.reviews.all()
            if not reviews:
                return None
            
            # Safely calculate total
            total = 0
            count = 0
            for review in reviews:
                try:
                    if review.rating is not None:
                        total += float(review.rating)
                        count += 1
                except (TypeError, ValueError):
                    continue
            
            if count == 0:
                return None
            
            return round(total / count, 1)
        except Exception as e:
            logger.error(f"Error in average_rating for book {self.id}: {e}")
            return None

    def review_count(self):
        """Return the total number of reviews for this book."""
        try:
            return self.reviews.count()
        except Exception as e:
            logger.error(f"Error in review_count for book {self.id}: {e}")
            return 0
    
    def is_from_api(self):
        """Return True if this book was imported from Google Books API."""
        return not self.is_indie and self.google_books_id is not None