"""
Form classes for the reviews app.

This module handles form validation and rendering for book reviews,
including the custom half-star rating system.
"""

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Form for creating and editing book reviews with half-star ratings.
    
    Features:
    - 0.5-star increments from 0 to 5 stars
    - Custom validation for rating values
    - Clean, Bootstrap-ready widgets
    - Placeholder text for better UX
    """
    
    # =========================================================================
    # RATING CHOICES (0 to 5 stars in 0.5 increments)
    # =========================================================================
    RATING_CHOICES = [
        (0.0, '0 Stars'),
        (0.5, '½ Star'),
        (1.0, '1 Star'),
        (1.5, '1½ Stars'),
        (2.0, '2 Stars'),
        (2.5, '2½ Stars'),
        (3.0, '3 Stars'),
        (3.5, '3½ Stars'),
        (4.0, '4 Stars'),
        (4.5, '4½ Stars'),
        (5.0, '5 Stars'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Rating selection'
        }),
        help_text="Select your rating (½ star increments available)"
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content']
        
        # =====================================================================
        # FIELD WIDGETS
        # =====================================================================
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize your review in a catchy title',
                'maxlength': 200,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your thoughts about the book... What did you like? What could be better?',
                'maxlength': 5000,
            }),
        }
        
        # =====================================================================
        # FIELD LABELS
        # =====================================================================
        labels = {
            'rating': 'Rating',
            'title': 'Review Title',
            'content': 'Your Review',
        }
        
        # =====================================================================
        # HELP TEXT
        # =====================================================================
        help_texts = {
            'title': 'Choose a title. Witty, funny, helpful, anything! Max length: 200 characters.',
            'content': 'Be specific and helpful to other readers. Max length: 5000 characters.',
        }
    
    # =========================================================================
    # CUSTOM VALIDATION
    # =========================================================================
    
    def clean_rating(self):
        """
        Validate that the rating is a valid choice.
        
        Returns:
            float: The validated rating value.
            
        Raises:
            ValidationError: If rating is invalid.
        """
        rating = self.cleaned_data.get('rating')
        
        if not rating:
            raise forms.ValidationError("Please select a rating.")
        
        # Convert to float for validation
        try:
            rating_float = float(rating)
        except (TypeError, ValueError):
            raise forms.ValidationError("Invalid rating value.")
        
        # Check if it's a valid half-star increment
        valid_ratings = [choice[0] for choice in self.RATING_CHOICES]
        if rating_float not in valid_ratings:
            raise forms.ValidationError(
                f"Rating must be one of: {', '.join(str(r) for r in valid_ratings)}"
            )
        
        return rating_float
    
    def clean_title(self):
        """
        Validate and clean the review title.
        
        Returns:
            str: The cleaned title.
            
        Raises:
            ValidationError: If title is too short or invalid.
        """
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise forms.ValidationError("Please provide a review title.")
        
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        
        if len(title) > 200:
            raise forms.ValidationError("Title cannot exceed 200 characters.")
        
        return title
    
    def clean_content(self):
        """
        Validate and clean the review content.
        
        Returns:
            str: The cleaned content.
            
        Raises:
            ValidationError: If content is too short.
        """
        content = self.cleaned_data.get('content', '').strip()
        
        if not content:
            raise forms.ValidationError("Please write your review.")
        
        if len(content) < 10:
            raise forms.ValidationError(
                "Review must be at least 10 characters long. "
                "Share a bit more about your thoughts!"
            )
        
        if len(content) > 5000:
            raise forms.ValidationError("Review cannot exceed 5000 characters.")
        
        return content
    
    def clean(self):
        """
        Cross-field validation.
        
        Ensures all fields are valid together.
        """
        cleaned_data = super().clean()
        
        # Add any cross-field validation here if needed in the future
        
        return cleaned_data