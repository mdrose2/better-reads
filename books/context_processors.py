# books/context_processors.py
"""
Context processors for the books app.
Makes book-related session data available to all templates.
"""

def pending_book(request):
    """
    Add pending book information to template context if it exists in session.
    Used for displaying login prompts with book-specific links.
    """
    context = {}
    
    if request.session.get('pending_book_slug'):
        context['pending_book'] = {
            'slug': request.session.get('pending_book_slug'),
            'title': request.session.get('pending_book_title'),
        }
    
    return context