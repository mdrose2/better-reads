"""
Google Books API integration utilities.

This module provides a robust interface for interacting with the Google Books API,
handling authentication, data parsing, rate limiting, and caching.
"""

import requests
import time
import random
import logging
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Simple in-memory cache for search results to reduce API calls
_search_cache = {}
_cache_time = {}


class GoogleBooksAPI:
    """
    Utility class for interacting with the Google Books API.
    
    Features:
    - Search for books by query string
    - Fetch specific books by Google Books ID
    - Parse API responses into Book model format
    - Exponential backoff retry logic for rate limiting
    - Result caching to minimize API usage
    
    Attributes:
        BASE_URL (str): The base URL for the Google Books API v1 endpoint.
        api_key (str): Google Books API key from settings.
    """
    
    BASE_URL = "https://www.googleapis.com/books/v1"
    
    def __init__(self):
        """Initialize the API client with the configured API key."""
        self.api_key = settings.GOOGLE_BOOKS_API_KEY
        
        # Enhanced logging for debugging API key issues
        if not self.api_key:
            logger.error("❌ Google Books API key is not configured in settings")
            logger.error("Check that GOOGLE_BOOKS_API_KEY is set in environment variables")
        else:
            # Log first few characters to confirm key is loaded (without exposing full key)
            logger.info(f"✅ Google Books API key loaded (starts with: {self.api_key[:5]}...)")
    
    def search_books(self, query, max_results=20, max_retries=3):
        """
        Search for books with caching and exponential backoff retry logic.
        
        Handles IP-based rate limiting gracefully by retrying with delays.
        Caches successful results for 10 minutes to reduce API calls.
        
        Args:
            query (str): Search query (title, author, ISBN, etc.)
            max_results (int): Maximum number of results to return
            max_retries (int): Number of retry attempts for rate limiting
            
        Returns:
            list: List of book items from the API, or empty list if search fails.
        """
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []
        
        logger.info(f"🔍 Searching books with query: '{query}'")
        
        # Check cache first (10-minute cache to reduce API calls)
        cache_key = f"{query}_{max_results}"
        if cache_key in _search_cache:
            cache_age = datetime.now() - _cache_time.get(cache_key, datetime.now())
            if cache_age < timedelta(minutes=10):
                logger.info(f"📦 Returning cached results for: '{query}'")
                return _search_cache[cache_key]
        
        # Implement exponential backoff retry logic
        for attempt in range(max_retries):
            try:
                # Add jitter to avoid synchronized retries
                sleep_time = random.uniform(0.5, 1.5) * (attempt + 1)
                logger.debug(f"Attempt {attempt + 1}/{max_retries} - waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
                results = self._make_api_call(query, max_results)
                
                # Cache successful results
                _search_cache[cache_key] = results
                _cache_time[cache_key] = datetime.now()
                
                logger.info(f"✅ Search successful - found {len(results)} results")
                return results
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
                
                if status_code == 429:
                    logger.warning(f"⚠️ Rate limited (attempt {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:
                        # Exponential backoff: wait longer between each retry
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"⏳ Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                    else:
                        logger.error("❌ Max retries exceeded for rate limit")
                        return []
                else:
                    # Log other HTTP errors
                    logger.error(f"❌ HTTP error {status_code} from Google Books API: {e}")
                    
                    # Provide specific guidance based on status code
                    if status_code == 403:
                        logger.error("🔑 API key may be invalid or quota exceeded")
                    elif status_code == 404:
                        logger.error("🔍 API endpoint not found")
                    raise
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    logger.error("❌ Max retries exceeded for timeout")
                    return []
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Connection error (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    logger.error("❌ Max retries exceeded for connection error")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error in API call: {e}", exc_info=True)
                if attempt == max_retries - 1:
                    return []
        
        return []  # Fallback return
    
    def _make_api_call(self, query, max_results):
        """
        Execute the actual API call to Google Books.
        
        Args:
            query (str): Search query
            max_results (int): Maximum results to return
            
        Returns:
            list: Raw book items from the API response
            
        Raises:
            requests.exceptions.RequestException: For network/HTTP errors
        """
        endpoint = f"{self.BASE_URL}/volumes"
        params = {
            'q': query.strip(),
            'key': self.api_key,
            'maxResults': min(max_results, 40),  # API max is 40
            'printType': 'books',
            'projection': 'full'
        }
        
        # Log sanitized parameters (hide full API key)
        safe_params = params.copy()
        safe_params['key'] = '***HIDDEN***'
        logger.debug(f"🌐 Making API call to {endpoint}")
        logger.debug(f"📤 Request params: {safe_params}")
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            logger.info(f"📥 Response status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            total_items = data.get('totalItems', 0)
            logger.info(f"📚 Found {len(items)} items (total: {total_items}) for query: '{query}'")
            
            # Log first result title for debugging if available
            if items and len(items) > 0:
                first_title = items[0].get('volumeInfo', {}).get('title', 'Unknown')
                logger.debug(f"🔖 First result title: '{first_title}'")
            
            return items
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error in API call: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text[:500]}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error in _make_api_call: {e}")
            raise
    
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
        
        logger.info(f"🔍 Fetching book with ID: {google_books_id}")
        endpoint = f"{self.BASE_URL}/volumes/{google_books_id}"
        params = {'key': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            logger.info(f"📥 Response status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            title = data.get('volumeInfo', {}).get('title', 'Unknown')
            logger.info(f"✅ Successfully fetched book: '{title}'")
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.info(f"📭 Book not found with ID: {google_books_id}")
            else:
                logger.error(f"❌ HTTP error fetching book {google_books_id}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching book {google_books_id}: {e}")
            return None
    
    def parse_book_data(self, api_data):
        """
        Convert Google Books API response into Book model format.
        
        Args:
            api_data (dict): Raw JSON response from Google Books API for a single book.
        
        Returns:
            dict: Cleaned and normalized book data ready for model creation.
        """
        if not api_data:
            logger.warning("Empty API data provided to parse_book_data")
            return {}
        
        volume_info = api_data.get('volumeInfo', {})
        book_id = api_data.get('id', 'Unknown')
        logger.debug(f"📖 Parsing book data for ID: {book_id}")
        
        # ======================================================================
        # Parse publication date (handles various formats)
        # ======================================================================
        published_date = None
        date_str = volume_info.get('publishedDate')
        if date_str:
            try:
                if len(date_str) == 4:      # Just year
                    published_date = datetime.strptime(date_str, '%Y').date()
                elif len(date_str) == 7:    # Year-month
                    published_date = datetime.strptime(date_str, '%Y-%m').date()
                else:                       # Full date
                    published_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                logger.debug(f"📅 Parsed date: {published_date}")
            except ValueError as e:
                logger.warning(f"⚠️ Could not parse date '{date_str}': {e}")
        
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
                logger.debug(f"📚 Found ISBN-13: {isbn_13}")
            elif id_type == 'ISBN_10':
                isbn_10 = id_value
                logger.debug(f"📚 Found ISBN-10: {isbn_10}")
        
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
        
        if cover_url:
            logger.debug(f"🖼️ Found cover image URL")
        
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
        
        logger.info(f"✅ Successfully parsed book data for: '{parsed_data['title']}'")
        return parsed_data
    
    def is_valid_isbn(self, isbn):
        """
        Simple validation for ISBN format.
        
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
            is_valid = len(clean_isbn) in [10, 13]
            logger.debug(f"🔢 ISBN '{isbn}' valid: {is_valid}")
            return is_valid
        
        logger.debug(f"🔢 ISBN '{isbn}' invalid: contains non-digit characters")
        return False