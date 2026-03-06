"""
URL patterns for the reviews app.

This module defines all URL routes for review-related functionality including:
- Listing all reviews
- Viewing, creating, updating, and deleting reviews
"""

from django.urls import path
from . import views

app_name = 'reviews'

# ==============================================================================
# URL PATTERNS
# ==============================================================================
# Note: Slug-based URLs must come after hard-coded paths
# to prevent pattern conflicts.

urlpatterns = [
    
    # ==========================================================================
    # REVIEW LISTINGS
    # ==========================================================================
    path('', 
         views.ReviewListView.as_view(), 
         name='list'),
    path('community/', 
         views.CommunityReviewsView.as_view(), 
         name='community'),
    
    # ==========================================================================
    # REVIEW CREATION (uses book_id, not slug)
    # ==========================================================================
    path('create/<int:book_id>/', 
         views.ReviewCreateView.as_view(), 
         name='create'),
    
    # ==========================================================================
    # REVIEW DETAIL & MANAGEMENT (slug-based)
    # ==========================================================================
    # Review detail view
    path('<slug:slug>/', 
         views.ReviewDetailView.as_view(), 
         name='detail'),
    
    # Review update
    path('<slug:slug>/update/', 
         views.ReviewUpdateView.as_view(), 
         name='update'),
    
    # Review deletion
    path('<slug:slug>/delete/', 
         views.ReviewDeleteView.as_view(), 
         name='delete'),
]