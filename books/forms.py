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