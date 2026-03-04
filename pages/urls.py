"""
URL patterns for the pages app.

This module defines routes for static and semi-static pages
like the home page, about page, etc.
"""

from django.urls import path
from . import views

app_name = 'pages'

# ==============================================================================
# URL PATTERNS
# ==============================================================================

urlpatterns = [
    # Home page - root URL of the site
    path('', 
         views.HomePageView.as_view(), 
         name='home'),
]