from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from books.models import Book
from reviews.models import Review
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class HomePageView(TemplateView):
    """
    Display the site's home page with aggregated statistics and featured content.
    Includes comprehensive error handling to prevent 500 errors.
    """
    
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Add aggregated data to the template context with error handling.
        """
        context = super().get_context_data(**kwargs)
        
        # ======================================================================
        # FEATURED CONTENT - with error handling
        # ======================================================================
        
        try:
            context['featured_books'] = Book.objects.all().order_by('-created_at')[:6]
            logger.info(f"Featured books loaded: {len(context['featured_books'])}")
        except Exception as e:
            logger.error(f"Error loading featured books: {e}")
            context['featured_books'] = []
        
        # Recent reviews - all reviews are visible
        try:
            context['recent_reviews'] = Review.objects.select_related(
                'user', 'book'
            ).order_by('-created_at')[:5]
            logger.info(f"Recent reviews loaded: {len(context['recent_reviews'])}")
        except Exception as e:
            logger.error(f"Error loading recent reviews: {e}")
            context['recent_reviews'] = []
        
        # ======================================================================
        # SITE STATISTICS - with error handling
        # ======================================================================
        
        try:
            context['total_books'] = Book.objects.count()
        except Exception as e:
            logger.error(f"Error counting books: {e}")
            context['total_books'] = 0
        
        try:
            context['total_reviews'] = Review.objects.count()
        except Exception as e:
            logger.error(f"Error counting reviews: {e}")
            context['total_reviews'] = 0
        
        try:
            # Count only active users (not anonymized)
            context['total_users'] = User.objects.filter(is_anonymized=False).count()
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            context['total_users'] = 0
        
        return context