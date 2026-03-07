from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import User
from .forms import CustomUserCreationForm, UserProfileForm


class CustomUserAdmin(UserAdmin):
    """
    Enhanced admin interface for the User model with search, filters, and actions.
    """
    
    add_form = CustomUserCreationForm
    form = UserProfileForm
    model = User
    
    # =========================================================================
    # LIST DISPLAY - What shows in the table view
    # =========================================================================
    list_display = (
        'id',
        'profile_picture_preview',
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'status_display',
        'email_verified',
        'date_joined_display',
        # 'review_count_display',  # Commented out
    )
    
    list_display_links = ('username', 'email')
    
    # =========================================================================
    # FILTERS - Sidebar filters
    # =========================================================================
    list_filter = (
        'is_staff',
        'is_superuser', 
        'is_active', 
        'email_verified',
        'is_anonymized',
        'date_joined',
        'last_active',
    )
    
    # =========================================================================
    # SEARCH - Searchable fields
    # =========================================================================
    search_fields = (
        'username', 
        'email', 
        'first_name', 
        'last_name',
        'id',
    )
    
    # =========================================================================
    # DATE HIERARCHY - Date drill-down
    # =========================================================================
    date_hierarchy = 'date_joined'
    
    # =========================================================================
    # ACTIONS - Bulk operations
    # =========================================================================
    actions = ['make_active', 'make_inactive', 'verify_emails', 'anonymize_users']
    
    # =========================================================================
    # CUSTOM QUERYSET FOR SORTING
    # =========================================================================
    def get_queryset(self, request):
        """Annotate queryset with review count for sorting."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            review_count=Count('reviews')
        )
    
    # =========================================================================
    # CUSTOM METHODS FOR DISPLAY
    # =========================================================================
    
    def profile_picture_preview(self, obj):
        """Show small profile picture preview."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html('<div style="width: 30px; height: 30px; background: #e9ecef; border-radius: 50%; display: flex; align-items: center; justify-content: center;">👤</div>')
    profile_picture_preview.short_description = 'Pic'
    profile_picture_preview.admin_order_field = 'id'
    
    def date_joined_display(self, obj):
        """Format date nicely with icon."""
        return format_html(
            '<span title="{}">{}</span>',
            obj.date_joined,
            obj.date_joined.strftime('%Y-%m-%d')
        )
    date_joined_display.short_description = 'Joined'
    date_joined_display.admin_order_field = 'date_joined'
    
    def status_display(self, obj):
        """Display user status with badges."""
        if not obj.is_active:
            return format_html('<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px;">Inactive</span>')
        if obj.is_superuser:
            return format_html('<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px;">Admin</span>')
        if obj.is_staff:
            return format_html('<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px;">Staff</span>')
        return format_html('<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px;">Active</span>')
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'is_active'
    
    def review_count_display(self, obj):
        """Show number of reviews with link."""
        count = getattr(obj, 'review_count', obj.reviews.count())
        if count > 0:
            return format_html(
                '<a href="/admin/reviews/review/?user__id={}" style="color: #28a745; font-weight: 600;">{}</a>',
                obj.id,
                count
            )
        return '—'
    review_count_display.short_description = 'Reviews'
    review_count_display.admin_order_field = 'review_count'
    
    # =========================================================================
    # CUSTOM ACTIONS
    # =========================================================================
    
    def make_active(self, request, queryset):
        """Bulk activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ {updated} user(s) activated successfully.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        """Bulk deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'✅ {updated} user(s) deactivated successfully.')
    make_inactive.short_description = "Deactivate selected users"
    
    def verify_emails(self, request, queryset):
        """Bulk verify emails."""
        updated = queryset.update(email_verified=True)
        self.message_user(request, f'✅ {updated} user(s) email verified.')
    verify_emails.short_description = "Verify email for selected users"
    
    def anonymize_users(self, request, queryset):
        """Bulk anonymize users (privacy-preserving deletion)."""
        for user in queryset:
            user.anonymize()
        self.message_user(request, f'✅ {queryset.count()} user(s) anonymized.')
    anonymize_users.short_description = "Anonymize selected users"
    
    # =========================================================================
    # FIELDSET ORGANIZATION - Edit page layout
    # =========================================================================
    # Override fieldsets to exclude usable_password
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_anonymized', 'email_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_active')}),
    )
    
    # Override add_fieldsets for the "Add user" page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'bio', 'profile_picture'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified'),
        }),
    )
    
    readonly_fields = (
        'date_joined',
        'last_login',
        'last_active',
        'is_anonymized',
    )


admin.site.register(User, CustomUserAdmin)