"""
URL patterns for the books app.

This module defines all URL routes for book-related functionality including:
- Searching for books via Google Books API
- Viewing community and personal libraries
- Adding, editing, and deleting books
- Managing indie book submissions
"""

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # ==========================================================================
    # PERSONAL LIBRARY (Requires login)
    # ==========================================================================
    path('my-library/', 
         views.MyLibraryView.as_view(), 
         name='my-library'),

    # ==========================================================================
    # INDIE BOOK SUBMISSIONS (Requires login)
    # ==========================================================================
    path('add/indie/', 
         views.IndieBookCreateView.as_view(), 
         name='add-indie'),
    
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
    # BOOK DETAIL & MANAGEMENT
    # ==========================================================================
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
    # COMMUNITY LIBRARY (All books - public)
    # ==========================================================================
    path('', 
         views.AllBooksListView.as_view(), 
         name='list'),
]