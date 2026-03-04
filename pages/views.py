"""
View classes for the pages app.

This module handles static and semi-static pages including the home page,
which aggregates data from multiple apps to create a dashboard experience.
"""

from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from books.models import Book
from reviews.models import Review

User = get_user_model()


class HomePageView(TemplateView):
    """
    Display the site's home page with aggregated statistics and featured content.
    
    This view provides a dashboard-like experience showing:
    - Featured/recently added books
    - Recent reviews from the community
    - Site-wide statistics (total books, reviews, users)
    
    Template: pages/home.html
    Context:
        - featured_books: 6 most recently added books
        - recent_reviews: 5 most recent reviews with user and book details
        - total_books: Total number of books in the library
        - total_reviews: Total number of reviews written
        - total_users: Total number of registered users
    """
    
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Add aggregated data to the template context.
        
        Returns:
            dict: Context dictionary with featured books, recent reviews,
                  and site-wide statistics.
        """
        context = super().get_context_data(**kwargs)
        
        # ======================================================================
        # FEATURED CONTENT
        # ======================================================================
        
        # Recently added books (limit to 6 for grid layout)
        context['featured_books'] = Book.objects.all().order_by('-created_at')[:6]
        
        # Recent reviews with optimized queries (select_related prevents N+1 queries)
        context['recent_reviews'] = Review.objects.select_related(
            'user', 'book'
        ).order_by('-created_at')[:5]
        
        # ======================================================================
        # SITE STATISTICS
        # ======================================================================
        
        context['total_books'] = Book.objects.count()
        context['total_reviews'] = Review.objects.count()
        context['total_users'] = User.objects.count()
        
        return context