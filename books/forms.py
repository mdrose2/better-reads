"""
Form classes for the books app.
Handles validation and rendering for book-related forms.
"""

from django import forms
from .models import Book


class IndieBookForm(forms.ModelForm):
    """
    Form for users to add independent/indie books to the library.
    
    This form allows users to contribute books not found in the Google Books API.
    The authors field accepts comma-separated text and is automatically
    converted to JSON format for storage.
    """
    
    # Override the authors field to accept plain text
    authors = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "Patrick Rothfuss" or "Jane Austen, Charlotte Brontë"',
            'required': True,
        }),
        help_text="For multiple authors, separate names with commas"
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 
            'authors', 
            'publisher', 
            'description', 
            'isbn_13', 
            'page_count'
        ]
        
        # =====================================================================
        # FIELD WIDGETS
        # =====================================================================
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "The Name of the Wind"',
                'autofocus': True,
            }),
            
            'publisher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "DAW Books" (optional)',
            }),
            
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write a brief description of the book...',
            }),
            
            'isbn_13': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 9780756404741 (optional)',
            }),
            
            'page_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 662 (optional)',
                'min': 1,
            }),
        }
        
        # =====================================================================
        # FIELD LABELS
        # =====================================================================
        labels = {
            'title': 'Book Title',
            'authors': 'Author(s)',
            'publisher': 'Publisher',
            'description': 'Description',
            'isbn_13': 'ISBN-13',
            'page_count': 'Page Count',
        }
        
        # =====================================================================
        # HELP TEXT
        # =====================================================================
        help_texts = {
            'publisher': 'Publisher name (optional)',
            'isbn_13': '13-digit ISBN (optional but helpful for identification)',
            'page_count': 'Total number of pages (optional)',
        }
    
    # =========================================================================
    # CUSTOM VALIDATION AND DATA CONVERSION
    # =========================================================================
    
    def clean_authors(self):
        """
        Convert comma-separated author string to JSON-compatible list.
        
        This method:
        1. Takes the plain text input from the form
        2. Splits by commas
        3. Strips whitespace from each author name
        4. Returns a list (which will be stored as JSON)
        """
        authors_str = self.cleaned_data.get('authors', '')
        
        if not authors_str or not authors_str.strip():
            raise forms.ValidationError("At least one author is required.")
        
        # Split by commas and clean each author name
        author_list = [a.strip() for a in authors_str.split(',') if a.strip()]
        
        if not author_list:
            raise forms.ValidationError("Please enter at least one valid author name.")
        
        # Log the conversion for debugging (optional)
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Converted authors '{authors_str}' to list: {author_list}")
        
        return author_list  # Django will automatically serialize this to JSON
    
    def clean_title(self):
        """Validate that the title is not just whitespace."""
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError("Book title cannot be empty.")
        return title.strip()
    
    def clean_isbn_13(self):
        """
        Validate ISBN-13 format if provided.
        Should be 13 digits, optionally with hyphens.
        """
        isbn = self.cleaned_data.get('isbn_13')
        if not isbn:
            return isbn
        
        # Remove common separators
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        
        # Check if it's all digits
        if not clean_isbn.isdigit():
            raise forms.ValidationError("ISBN must contain only numbers and hyphens.")
        
        # Check length
        if len(clean_isbn) != 13:
            raise forms.ValidationError("ISBN-13 must be exactly 13 digits.")
        
        return clean_isbn
    
    def clean_page_count(self):
        """
        Validate page count if provided.
        Must be a positive integer.
        """
        page_count = self.cleaned_data.get('page_count')
        if page_count is not None and page_count < 1:
            raise forms.ValidationError("Page count must be at least 1.")
        return page_count

class BookEditForm(forms.ModelForm):
    """
    Form for editing books (both admin and indie creators).
    
    This form handles the authors field as plain text, converting
    between string and JSON format automatically.
    """
    
    # Override authors field to accept plain text
    authors = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "Patrick Rothfuss" or "Jane Austen, Charlotte Brontë"',
            'required': True,
        }),
        help_text="For multiple authors, separate names with commas"
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'authors', 'publisher', 'published_date',
            'description', 'page_count', 'categories', 'cover_image_url',
            'thumbnail_url', 'isbn_13', 'isbn_10'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book title'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book subtitle (optional)'
            }),
            'publisher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publisher name'
            }),
            'published_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Book description'
            }),
            'page_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of pages'
            }),
            'categories': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Fiction, Fantasy, Mystery (comma separated)'
            }),
            'cover_image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL to cover image'
            }),
            'thumbnail_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL to thumbnail image'
            }),
            'isbn_13': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '978-1234567890'
            }),
            'isbn_10': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789X'
            }),
        }
        
        labels = {
            'title': 'Book Title',
            'subtitle': 'Subtitle',
            'authors': 'Author(s)',
            'publisher': 'Publisher',
            'published_date': 'Publication Date',
            'description': 'Description',
            'page_count': 'Page Count',
            'categories': 'Categories',
            'cover_image_url': 'Cover Image URL',
            'thumbnail_url': 'Thumbnail URL',
            'isbn_13': 'ISBN-13',
            'isbn_10': 'ISBN-10',
        }
        
        help_texts = {
            'published_date': 'Format: YYYY-MM-DD',
            'categories': 'Separate multiple categories with commas',
            'isbn_13': '13-digit ISBN (optional)',
            'isbn_10': '10-digit ISBN (optional)',
        }
    
    def clean_authors(self):
        """
        Convert comma-separated author string to JSON-compatible list.
        """
        authors_str = self.cleaned_data.get('authors', '')
        
        if not authors_str or not authors_str.strip():
            raise forms.ValidationError("At least one author is required.")
        
        # Split by commas and clean each author name
        author_list = [a.strip() for a in authors_str.split(',') if a.strip()]
        
        if not author_list:
            raise forms.ValidationError("Please enter at least one valid author name.")
        
        return author_list
    
    def clean_categories(self):
        """
        Convert comma-separated categories string to JSON-compatible list.
        """
        categories_str = self.cleaned_data.get('categories', '')
        if not categories_str:
            return []
        
        # Split by commas and clean each category
        category_list = [c.strip() for c in categories_str.split(',') if c.strip()]
        return category_list
    
    def clean_isbn_13(self):
        """Validate ISBN-13 format if provided."""
        isbn = self.cleaned_data.get('isbn_13')
        if not isbn:
            return isbn
        
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        if not clean_isbn.isdigit():
            raise forms.ValidationError("ISBN must contain only numbers and hyphens.")
        if len(clean_isbn) != 13:
            raise forms.ValidationError("ISBN-13 must be exactly 13 digits.")
        return clean_isbn
    
    def clean_isbn_10(self):
        """Validate ISBN-10 format if provided."""
        isbn = self.cleaned_data.get('isbn_10')
        if not isbn:
            return isbn
        
        clean_isbn = isbn.replace('-', '').replace(' ', '')
        if not clean_isbn.isdigit() and not clean_isbn[-1].upper() == 'X':
            # ISBN-10 can end with 'X'
            if not clean_isbn[:-1].isdigit():
                raise forms.ValidationError("ISBN-10 must contain only numbers and hyphens, may end with X.")
        if len(clean_isbn) != 10:
            raise forms.ValidationError("ISBN-10 must be exactly 10 characters.")
        return clean_isbn