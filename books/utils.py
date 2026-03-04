"""
Google Books API integration utilities.

This module provides a clean interface for interacting with the Google Books API,
handling authentication, data parsing, and error management.
"""

import requests
from django.conf import settings
from datetime import datetime
import logging

# Set up logging for API interactions
logger = logging.getLogger(__name__)


class GoogleBooksAPI:
    """
    Utility class for interacting with the Google Books API.
    
    This class handles all communication with the Google Books API, including:
    - Searching for books by query string
    - Fetching specific books by Google Books ID
    - Parsing API responses into a format compatible with the Book model
    
    Attributes:
        BASE_URL (str): The base URL for the Google Books API v1 endpoint.
        api_key (str): Google Books API key from settings.
    """
    
    BASE_URL = "https://www.googleapis.com/books/v1"
    
    def __init__(self):
        """Initialize the API client with the configured API key."""
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
        if not self.api_key:
            logger.warning("Google Books API key is not configured")
    
    def search_books(self, query, max_results=20):
        """
        Search for books by title, author, or ISBN.
        
        Args:
            query (str): Search query (title, author, ISBN, etc.)
            max_results (int): Maximum number of results to return (default: 20, max: 40)
        
        Returns:
            list: List of book items from the API, or empty list if search fails.
        """
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []
        
        endpoint = f"{self.BASE_URL}/volumes"
        params = {
            'q': query.strip(),
            'key': self.api_key,
            'maxResults': min(max_results, 40),  # API max is 40
            'printType': 'books',
            'projection': 'full'
        }
        
        try:
            logger.debug(f"Searching books with query: {query}")
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            logger.info(f"Found {len(items)} results for query: {query}")
            return items
            
        except requests.exceptions.Timeout:
            logger.error("Google Books API request timed out")
            return []
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Google Books API")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Google Books API: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Unexpected error calling Google Books API: {e}")
            return []
    
    def get_book_by_id(self, google_books_id):
        """
        Fetch a specific book by its Google Books ID.
        
        Args:
            google_books_id (str): The unique Google Books identifier.
        
        Returns:
            dict: Complete book data from API, or None if not found/error.
        """
        if not google_books_id:
            logger.warning("Empty Google Books ID provided")
            return None
        
        endpoint = f"{self.BASE_URL}/volumes/{google_books_id}"
        params = {'key': self.api_key}
        
        try:
            logger.debug(f"Fetching book with ID: {google_books_id}")
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.info(f"Book not found with ID: {google_books_id}")
            else:
                logger.error(f"HTTP error fetching book {google_books_id}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching book {google_books_id}: {e}")
            return None
    
    def parse_book_data(self, api_data):
        """
        Convert Google Books API response into a format compatible with Book model.
        
        Args:
            api_data (dict): Raw JSON response from Google Books API for a single book.
        
        Returns:
            dict: Cleaned and normalized book data ready for model creation.
        """
        if not api_data:
            logger.warning("Empty API data provided to parse_book_data")
            return {}
        
        volume_info = api_data.get('volumeInfo', {})
        
        # ======================================================================
        # Parse publication date (handles various formats)
        # ======================================================================
        published_date = None
        date_str = volume_info.get('publishedDate')
        if date_str:
            try:
                # Handle different date formats from Google Books
                if len(date_str) == 4:  # Just year
                    published_date = datetime.strptime(date_str, '%Y').date()
                elif len(date_str) == 7:  # Year-month
                    published_date = datetime.strptime(date_str, '%Y-%m').date()
                else:  # Full date
                    published_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError as e:
                logger.warning(f"Could not parse date '{date_str}': {e}")
        
        # ======================================================================
        # Extract ISBN identifiers
        # ======================================================================
        isbn_13 = None
        isbn_10 = None
        for identifier in volume_info.get('industryIdentifiers', []):
            id_type = identifier.get('type')
            id_value = identifier.get('identifier')
            
            if id_type == 'ISBN_13':
                isbn_13 = id_value
            elif id_type == 'ISBN_10':
                isbn_10 = id_value
        
        # ======================================================================
        # Get image URLs (prioritize larger images)
        # ======================================================================
        image_links = volume_info.get('imageLinks', {})
        cover_url = (
            image_links.get('extraLarge') or
            image_links.get('large') or
            image_links.get('medium') or
            image_links.get('small') or
            image_links.get('thumbnail')
        )
        
        # ======================================================================
        # Build and return normalized book data
        # ======================================================================
        parsed_data = {
            'title': volume_info.get('title', '').strip(),
            'subtitle': volume_info.get('subtitle', '').strip() or None,
            'authors': volume_info.get('authors', []),
            'isbn_13': isbn_13,
            'isbn_10': isbn_10,
            'publisher': volume_info.get('publisher', '').strip() or None,
            'published_date': published_date,
            'description': volume_info.get('description', '').strip() or None,
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', []),
            'cover_image_url': cover_url,
            'thumbnail_url': image_links.get('thumbnail', ''),
            'google_books_id': api_data.get('id', ''),
        }
        
        logger.debug(f"Successfully parsed book data for: {parsed_data['title']}")
        return parsed_data
    
    def is_valid_isbn(self, isbn):
        """
        Simple validation for ISBN format (basic check).
        
        Args:
            isbn (str): ISBN string to validate.
        
        Returns:
            bool: True if ISBN appears valid, False otherwise.
        """
        if not isbn:
            return False
        
        # Remove common separators
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        
        # Check if all digits and correct length
        if clean_isbn.isdigit():
            return len(clean_isbn) in [10, 13]
        
        return False