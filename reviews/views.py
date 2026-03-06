"""
View classes for the reviews app.

This module contains all view logic for review-related functionality including:
- Listing all reviews
- Viewing individual reviews
- Creating, updating, and deleting reviews
- Permission handling for review authors
- Comprehensive error handling and logging
"""

import logging
import traceback
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Review
from books.models import Book
from .forms import ReviewForm

logger = logging.getLogger(__name__)


# ==============================================================================
# REVIEW LISTING VIEW
# ==============================================================================

class ReviewListView(ListView):
    """
    Display a paginated list of all reviews in the system.
    
    Used primarily for admin/stats pages. Optimized with select_related
    to prevent N+1 queries on user and book relationships.
    
    Template: reviews/review_list.html
    Context: 'reviews' (paginated list of Review objects)
    Pagination: 20 reviews per page
    """
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Optimize queries by fetching related user and book data.
        
        Returns:
            QuerySet: Reviews with user and book prefetched
        """
        return Review.objects.select_related('user', 'book').all()


# ==============================================================================
# REVIEW DETAIL VIEW
# ==============================================================================

class ReviewDetailView(DetailView):
    """
    Display a single review with full content.
    
    Uses slug for SEO-friendly URLs.
    
    Template: reviews/review_detail.html
    Context: 'review' (single Review object)
    URL Pattern: /reviews/<slug:slug>/
    """
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


# ==============================================================================
# REVIEW CREATE VIEW
# ==============================================================================

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new review for a specific book.
    
    Requires user to be logged in.
    Prevents duplicate reviews (one per user per book).
    Includes comprehensive error handling and logging.
    
    Template: reviews/review_form.html
    URL Pattern: /reviews/create/<int:book_id>/
    """
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_context_data(self, **kwargs):
        """
        Add the book being reviewed to template context.
        
        IMPORTANT: Do NOT access self.object here - it doesn't exist yet!
        This method only runs before the form is submitted.
        
        Returns:
            dict: Context with book object
        """
        context = super().get_context_data(**kwargs)
        book_id = self.kwargs.get('book_id')
        
        try:
            # Safely get the book being reviewed
            book = get_object_or_404(Book, id=book_id)
            context['book'] = book
            logger.info(f"ReviewCreateView: Loaded book '{book.title}' (ID: {book_id})")
        except Exception as e:
            logger.error(f"ReviewCreateView: Error loading book {book_id}: {e}")
            logger.error(traceback.format_exc())
            messages.error(self.request, "The book you're trying to review doesn't exist.")
            # We'll handle the redirect in the get() method
        
        return context

    def get(self, request, *args, **kwargs):
        """
        Handle GET request with proper error handling.
        """
        try:
            # Verify the book exists before showing the form
            book_id = self.kwargs.get('book_id')
            book = get_object_or_404(Book, id=book_id)
            logger.info(f"ReviewCreateView: GET request for book '{book.title}'")
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"ReviewCreateView: Error in GET: {e}")
            logger.error(traceback.format_exc())
            messages.error(request, "The book you're trying to review doesn't exist.")
            return redirect('books:list')

    def form_valid(self, form):
        """
        Assign user and book to review, check for duplicates.
        
        Returns:
            HttpResponse: Redirect to book detail on success
        """
        # Get the book from the URL
        book_id = self.kwargs.get('book_id')
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            logger.error(f"ReviewCreateView: Book {book_id} not found during form_valid")
            messages.error(self.request, "The book you're trying to review doesn't exist.")
            return redirect('books:list')
        
        # Assign user and book to the review
        form.instance.user = self.request.user
        form.instance.book = book
        
        logger.info(f"ReviewCreateView: Creating review for book '{book.title}' by user {self.request.user}")
        
        # Check if user already reviewed this book
        existing_review = Review.objects.filter(
            user=self.request.user,
            book=book
        ).first()
        
        if existing_review:
            logger.warning(f"ReviewCreateView: User {self.request.user} already reviewed book {book_id}")
            messages.error(
                self.request,
                'You have already reviewed this book!'
            )
            return redirect('books:detail', slug=book.slug)
        
        try:
            response = super().form_valid(form)
            logger.info(f"ReviewCreateView: Review created successfully with ID: {self.object.id}")
            messages.success(
                self.request,
                'Your review has been posted!'
            )
            return response
        except Exception as e:
            logger.error(f"ReviewCreateView: Error saving review: {e}")
            logger.error(traceback.format_exc())
            messages.error(self.request, 'An error occurred while creating your review.')
            return redirect('books:detail', slug=book.slug)
    
    def get_success_url(self):
        """
        Redirect to book detail page after successful creation.
        
        Returns:
            str: URL of the reviewed book's detail page
        """
        return reverse_lazy('books:detail', kwargs={'slug': self.object.book.slug})


# ==============================================================================
# REVIEW UPDATE VIEW
# ==============================================================================

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit an existing review.
    
    Only the review author can edit.
    Includes error handling for non-existent reviews.
    
    Template: reviews/review_form.html
    URL Pattern: /reviews/<slug:slug>/update/
    """
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        """Allow only the review author to edit."""
        review = self.get_object()
        return self.request.user == review.user
    
    def get_context_data(self, **kwargs):
        """
        Add the associated book to template context.
        
        Returns:
            dict: Context with book object
        """
        context = super().get_context_data(**kwargs)
        if self.object:
            context['book'] = self.object.book
        return context
    
    def get_object(self, queryset=None):
        """
        Retrieve the review with error handling.
        
        Returns:
            Review: The review object or None if not found
        """
        try:
            return super().get_object(queryset)
        except Exception as e:
            logger.error(f"ReviewUpdateView.get_object error: {e}")
            logger.error(traceback.format_exc())
            messages.error(
                self.request,
                "Review not found. It may have been deleted."
            )
            return None
    
    def get(self, request, *args, **kwargs):
        """Handle GET with error handling for missing reviews."""
        review = self.get_object()
        if review is None:
            return redirect('books:list')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Add success message after successful update."""
        messages.success(
            self.request,
            'Your review has been updated!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Redirect to book detail page after successful update.
        
        Returns:
            str: URL of the reviewed book's detail page
        """
        return reverse_lazy('books:detail', kwargs={'slug': self.object.book.slug})


# ==============================================================================
# REVIEW DELETE VIEW
# ==============================================================================

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a review.
    
    Only the review author can delete.
    Shows confirmation page before deletion.
    Includes error handling for non-existent reviews.
    
    Template: reviews/review_confirm_delete.html
    URL Pattern: /reviews/<slug:slug>/delete/
    """
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        """Allow only the review author to delete."""
        review = self.get_object()
        return self.request.user == review.user
    
    def get_object(self, queryset=None):
        """
        Retrieve the review with error handling.
        
        Returns:
            Review: The review object or None if not found
        """
        try:
            return super().get_object(queryset)
        except Exception as e:
            logger.error(f"ReviewDeleteView.get_object error: {e}")
            logger.error(traceback.format_exc())
            messages.error(
                self.request,
                "Review not found. It may have been deleted."
            )
            return None
    
    def get(self, request, *args, **kwargs):
        """Handle GET with error handling for missing reviews."""
        review = self.get_object()
        if review is None:
            return redirect('books:list')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Handle POST with error handling and success message."""
        review = self.get_object()
        if review is None:
            return redirect('books:list')
        
        # Store book slug for redirect
        book_slug = review.book.slug
        book_title = review.book.title
        
        logger.info(f"ReviewDeleteView: Deleting review {review.id} for book '{book_title}'")
        
        # Perform deletion
        response = super().post(request, *args, **kwargs)
        
        messages.success(
            request,
            'Your review has been deleted.'
        )
        return response
    
    def get_success_url(self):
        """
        Redirect to book detail page after successful deletion.
        
        Note: This is called after deletion, so self.object is still available.
        
        Returns:
            str: URL of the book's detail page
        """
        return reverse_lazy('books:detail', kwargs={'slug': self.object.book.slug})