"""
URL patterns for the books app.

This module defines all URL routes for book-related functionality including:
- Searching for books via Google Books API
- Viewing, adding, editing, and deleting books
- Managing indie book submissions
"""

from django.urls import path
from . import views

app_name = 'books'

# ==============================================================================
# URL PATTERNS
# ==============================================================================
# IMPORTANT: Order matters! Specific patterns must come before dynamic/catch-all
# patterns to ensure correct routing.

urlpatterns = [
    
    # ==========================================================================
    # SEARCH & DISCOVERY
    # ==========================================================================
    path('search/', 
         views.BookSearchView.as_view(), 
         name='search'),
    
    path('add/<str:google_books_id>/', 
         views.AddBookFromAPIMixin.as_view(), 
         name='add-from-api'),
    
    # ==========================================================================
    # INDIE BOOK SUBMISSIONS
    # ==========================================================================
    path('add/indie/', 
         views.IndieBookCreateView.as_view(), 
         name='add-indie'),
    
    # ==========================================================================
    # BOOK DETAIL & MANAGEMENT
    # ==========================================================================
    # Book detail view (using slug for SEO-friendly URLs)
    path('<slug:slug>/', 
         views.BookDetailView.as_view(), 
         name='detail'),
    
    # Admin book management (superuser only)
    path('<slug:slug>/edit/', 
         views.BookUpdateView.as_view(), 
         name='edit'),
    
    path('<slug:slug>/delete/', 
         views.BookDeleteView.as_view(), 
         name='delete'),
    
    # Indie book management (for users who added the book)
    path('<slug:slug>/edit/indie/', 
         views.IndieBookUpdateView.as_view(), 
         name='edit-indie'),
    
    path('<slug:slug>/delete/indie/', 
         views.IndieBookDeleteView.as_view(), 
         name='delete-indie'),
    
    # ==========================================================================
    # BOOK LISTING (CATCH-ALL)
    # ==========================================================================
    # This must be last as it would match any URL not caught above
    path('', 
         views.BookListView.as_view(), 
         name='list'),
]