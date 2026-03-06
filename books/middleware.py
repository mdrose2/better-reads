from django.shortcuts import redirect
from django.urls import reverse
import logging
import re
from django.contrib import messages

logger = logging.getLogger(__name__)

class AnonymousBookRedirectMiddleware:
    """
    Middleware that catches 500 errors on book-related pages for anonymous users
    and redirects them to login instead of showing a 500 error page.
    
    This protects:
    - /books/<slug>/ (detail pages)
    - /books/<slug>/edit/ (edit pages)
    - /books/<slug>/delete/ (delete pages)
    - Any other book URL patterns
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request normally
        response = self.get_response(request)
        
        # Check if this is a 500 error for an anonymous user on a book URL
        if (response.status_code == 500 and 
            not request.user.is_authenticated and 
            self._is_book_url(request.path)):
            
            # Log the redirect for debugging
            logger.warning(f"Redirecting anonymous user from 500 error at {request.path} to login")

            # Add a message to inform the user why they are being redirected
            messages.info(
                request,
                'Please log in to view this book.')
            
            # Redirect to login with next parameter to return after login
            login_url = reverse('users:login')
            return redirect(f"{login_url}?next={request.path}")
        
        return response
    
    def _is_book_url(self, path):
        """
        Check if the URL path is a book-related URL.
        Returns True for paths like:
        - /books/frankenstein/
        - /books/frankenstein/edit/
        - /books/frankenstein/delete/
        """
        # Match any path that starts with /books/ and has at least one more segment
        book_pattern = r'^/books/[^/]+(/.*)?$'
        return bool(re.match(book_pattern, path))