"""
URL configuration for book_review_site project.

The `urlpatterns` list routes URLs to views. For more information see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Site pages
    path('', include('pages.urls')),      # Home page
    
    # App URLs
    path('books/', include('books.urls')),    # Book management
    path('reviews/', include('reviews.urls')), # Review management
    path('users/', include('users.urls')),     # User authentication
]