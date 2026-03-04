"""
Admin interface configuration for the users app.

This module registers the custom User model with the Django admin interface
and provides customized display, filtering, and editing options.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm


class CustomUserAdmin(UserAdmin):
    """
    Customized admin interface for the User model.
    
    Provides:
    - Custom forms for creation and editing
    - Configured list display with key fields
    - Search and filter capabilities
    - Organized field groupings for better UX
    """
    
    # Forms for add and change views
    add_form = CustomUserCreationForm
    form = UserProfileForm
    model = User
    
    # =========================================================================
    # LIST DISPLAY CONFIGURATION
    # =========================================================================
    
    list_display = (
        'email', 
        'username', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'email_verified'
    )
    
    list_filter = (
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'email_verified'
    )
    
    search_fields = (
        'username', 
        'email', 
        'first_name', 
        'last_name'
    )
    
    ordering = ('email',)
    
    # =========================================================================
    # EDIT FORM FIELDSETS
    # =========================================================================
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Email Verification', {
            'fields': ('email_verified',),
            'classes': ('collapse',)
        }),
    )
    
    # =========================================================================
    # ADD FORM FIELDSETS
    # =========================================================================
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            )
        }),
    )


# Register the model with custom admin
admin.site.register(User, CustomUserAdmin)