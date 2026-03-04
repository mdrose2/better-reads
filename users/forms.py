"""
Form classes for the users app.

This module handles form validation and rendering for:
- User registration
- Profile editing
- Password changes
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Form for new user registration.
    
    Extends Django's UserCreationForm to add:
    - Custom styling with Bootstrap classes
    - Email validation
    - Auto-unverified status for new users
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def clean_email(self):
        """
        Validate that the email is not already in use.
        
        Returns:
            str: The cleaned email address.
            
        Raises:
            ValidationError: If email already exists.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def save(self, commit=True):
        """
        Create the user with email_verified=False.
        
        Args:
            commit (bool): Whether to save to database immediately.
            
        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.email_verified = False  # New users start unverified
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.
    
    Handles:
    - Username changes with uniqueness validation
    - Personal information (first name, last name)
    - Bio with character limits
    - Profile picture uploads
    """
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'bio', 'profile_picture')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
                'id': 'id_username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'id': 'id_bio',
                'maxlength': 500
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_username(self):
        """
        Validate that the username is unique.
        
        Returns:
            str: The cleaned username.
            
        Raises:
            ValidationError: If username is already taken.
        """
        username = self.cleaned_data.get('username')
        
        # Check if username is taken by another user
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        
        return username