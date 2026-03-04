# books/context_processors.py
"""
Context processors for the books app.
Makes book-related session data available to all templates.
"""

import logging

logger = logging.getLogger(__name__)

def pending_book(request):
    """
    Add pending book information to template context if it exists in session.
    Used for displaying login prompts with book-specific links.
    
    This context processor is completely fail-safe - it will never throw
    an exception, even for anonymous users or when session is unavailable.
    """
    context = {}
    
    try:
        # Check if session exists and is accessible
        if not hasattr(request, 'session'):
            logger.debug("No session attribute on request")
            return context
        
        # Try to get the pending book data
        pending_slug = request.session.get('pending_book_slug')
        pending_title = request.session.get('pending_book_title')
        
        # Only add to context if both values exist
        if pending_slug and pending_title:
            context['pending_book'] = {
                'slug': pending_slug,
                'title': pending_title,
            }
            logger.debug(f"Pending book found: {pending_title}")
            
    except AttributeError as e:
        # Session might not be fully initialized
        logger.debug(f"Session not ready: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in pending_book context processor: {e}")
    
    return context