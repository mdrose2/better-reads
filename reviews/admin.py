from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.text import slugify
from .models import Review


# =============================================================================
# CUSTOM ADMIN FORM FOR REVIEW
# -----------------------------------------------------------------------------
# Auto-generates a slug from the title if not provided.
# =============================================================================
class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    def clean_slug(self):
        """If slug is empty, generate it from the title."""
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        if not slug and title:
            slug = slugify(title)
            # Ensure uniqueness (you may want to add a counter if needed)
            original_slug = slug
            counter = 1
            while Review.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
        return slug


class ReviewAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for Review model.
    """
    form = ReviewAdminForm  # Use custom form

    # =========================================================================
    # LIST DISPLAY
    # =========================================================================
    list_display = (
        'id',
        'book_link',
        'review_title',
        'user_link',
        'rating_display',
        'created_at_display',
        'edited_display',
        'content_preview',
    )

    list_display_links = ('review_title',)

    # =========================================================================
    # FILTERS
    # =========================================================================
    list_filter = (
        'rating',
        'created_at',
        'updated_at',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('book', admin.RelatedOnlyFieldListFilter),
    )

    # =========================================================================
    # SEARCH
    # =========================================================================
    search_fields = (
        'title',
        'content',
        'user__username',
        'user__email',
        'book__title',
        'book__authors',
        'id',
    )

    # =========================================================================
    # DATE HIERARCHY
    # =========================================================================
    date_hierarchy = 'created_at'

    # =========================================================================
    # ACTIONS
    # =========================================================================
    actions = ['delete_selected']

    # =========================================================================
    # CUSTOM QUERYSET FOR SORTING
    # =========================================================================
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'book')

    # =========================================================================
    # CUSTOM METHODS – with error handling
    # =========================================================================

    def book_link(self, obj):
        """Link to the book with proper admin URL."""
        try:
            if obj.book:
                url = reverse('admin:books_book_change', args=[obj.book.id])
                return format_html(
                    '<a href="{}" style="color: #28a745; font-weight: 500;">{}</a>',
                    url,
                    obj.book.title[:40] + ('...' if len(obj.book.title) > 40 else '')
                )
        except Exception:
            return '—'
        return '—'
    book_link.short_description = 'Book'
    book_link.admin_order_field = 'book__title'

    def review_title(self, obj):
        """Review title with slug."""
        try:
            return format_html(
                '<strong>{}</strong><br><small style="color: #6c757d;">/{}/</small>',
                obj.title[:30] + ('...' if len(obj.title) > 30 else ''),
                obj.slug
            )
        except Exception:
            return obj.title or '—'
    review_title.short_description = 'Review'
    review_title.admin_order_field = 'title'

    def user_link(self, obj):
        """Link to user with proper admin URL."""
        try:
            if obj.user:
                url = reverse('admin:users_user_change', args=[obj.user.id])
                return format_html(
                    '<a href="{}" style="color: #28a745;">@{}</a>',
                    url,
                    obj.user.username
                )
        except Exception:
            return '—'
        return format_html('<span style="color: #999;">deleted_user</span>')
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def rating_display(self, obj):
        """Show rating with stars."""
        try:
            stars = obj.get_star_rating()
        except AttributeError:
            # Fallback if method missing
            stars = '★' * obj.rating if obj.rating else ''
        return format_html(
            '<span style="color: #ffc107; font-size: 1.1rem;" title="{} stars">{}</span>',
            obj.rating,
            stars
        )
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'

    def created_at_display(self, obj):
        """Format creation date."""
        try:
            return format_html(
                '<span title="{}">{}</span>',
                obj.created_at,
                obj.created_at.strftime('%Y-%m-%d')
            )
        except Exception:
            return '—'
    created_at_display.short_description = 'Posted'
    created_at_display.admin_order_field = 'created_at'

    def edited_display(self, obj):
        """Show if edited."""
        try:
            if obj.is_edited():
                return format_html(
                    '<span style="color: #ffc107;" title="Edited">✓</span>'
                )
        except Exception:
            pass
        return format_html('<span style="color: #6c757d;">—</span>')
    edited_display.short_description = 'Edited'
    edited_display.admin_order_field = 'updated_at'

    def content_preview(self, obj):
        """Preview of review content."""
        try:
            preview = obj.content[:60] + ('...' if len(obj.content) > 60 else '')
            return format_html(
                '<span title="{}">{}</span>',
                obj.content,
                preview
            )
        except Exception:
            return '—'
    content_preview.short_description = 'Preview'

    # =========================================================================
    # FIELDSET ORGANIZATION
    # =========================================================================
    fieldsets = (
        ('Review Content', {
            'fields': (
                ('rating', 'title'),
                'content',
            ),
        }),
        ('Relationships', {
            'fields': (
                'user',
                'book',
            ),
        }),
        ('URL', {
            'fields': ('slug',),
            'classes': ('collapse',),  # Collapse by default
        }),
        ('Timestamps', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
        }),
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    # =========================================================================
    # OVERRIDE SAVE_MODEL TO ENSURE SLUG IS SET
    # =========================================================================
    def save_model(self, request, obj, form, change):
        """Ensure slug is set before saving."""
        if not obj.slug and obj.title:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)


admin.site.register(Review, ReviewAdmin)