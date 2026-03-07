from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import Book
import json


# =============================================================================
# CUSTOM ADMIN FORM FOR BOOK
# -----------------------------------------------------------------------------
# Converts authors/categories to/from comma‑separated strings,
# provides clear help text, and reserves space for error messages.
# =============================================================================
class BookAdminForm(forms.ModelForm):
    """
    Custom form for the Book model.

    - Authors and categories are entered as comma‑separated lists.
    - Stored internally as JSON strings.
    - Help text and fixed container heights prevent layout shift when errors appear.
    """

    authors = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'style': 'width: 600px;',
            'placeholder': 'John Doe, Jane Smith, Bob Johnson'
        }),
        help_text="Enter author names separated by commas. Example: 'John Doe, Jane Smith'",
        required=True
    )

    categories = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'style': 'width: 600px;',
            'placeholder': 'Fiction, Mystery, Science Fiction'
        }),
        help_text="Enter categories separated by commas (optional). Example: 'Fiction, Mystery'"
    )

    class Meta:
        model = Book
        fields = '__all__'          # Include all model fields

    def __init__(self, *args, **kwargs):
        """
        If editing an existing book, convert stored JSON back to comma‑separated
        strings for display in the form.
        """
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # --- Authors ---
            if self.instance.authors:
                try:
                    if isinstance(self.instance.authors, str):
                        authors_list = json.loads(self.instance.authors)
                    elif isinstance(self.instance.authors, list):
                        authors_list = self.instance.authors
                    else:
                        authors_list = []
                    self.initial['authors'] = ', '.join(authors_list)
                except (json.JSONDecodeError, TypeError):
                    # Fallback for legacy plain‑text data
                    self.initial['authors'] = self.instance.authors

            # --- Categories ---
            if self.instance.categories:
                try:
                    if isinstance(self.instance.categories, str):
                        categories_list = json.loads(self.instance.categories)
                    elif isinstance(self.instance.categories, list):
                        categories_list = self.instance.categories
                    else:
                        categories_list = []
                    self.initial['categories'] = ', '.join(categories_list)
                except (json.JSONDecodeError, TypeError):
                    self.initial['categories'] = self.instance.categories

    def clean_authors(self):
        """
        Convert the comma‑separated string back to a JSON array for storage.
        Raise a validation error if no valid author names are provided.
        """
        authors_text = self.cleaned_data['authors']
        if not authors_text.strip():
            raise forms.ValidationError("At least one author is required.")

        # Split, clean, and filter empty entries
        author_list = [a.strip() for a in authors_text.split(',') if a.strip()]

        if not author_list:
            raise forms.ValidationError("Please enter at least one valid author name.")

        return json.dumps(author_list)

    def clean_categories(self):
        """
        Convert the comma‑separated string to a JSON array.
        Return an empty JSON array if no input is given.
        """
        categories_text = self.cleaned_data.get('categories', '')
        if not categories_text or not categories_text.strip():
            return json.dumps([])

        category_list = [c.strip() for c in categories_text.split(',') if c.strip()]
        return json.dumps(category_list)


# =============================================================================
# BOOK ADMIN – ENHANCED INTERFACE
# -----------------------------------------------------------------------------
# All customisations for the book list display, filters, actions, and
# the edit form (via the form attribute).
# =============================================================================
class BookAdmin(admin.ModelAdmin):
    """
    Enhanced admin interface for the Book model.
    """

    # Use the custom form defined above
    form = BookAdminForm

    # =========================================================================
    # LIST DISPLAY
    # =========================================================================
    list_display = (
        'cover_thumbnail',
        'title_short',
        'author_short',
        'year',
        'rating_detailed',
        'indie_badge',
    )

    list_display_links = ('title_short',)

    # =========================================================================
    # LIST FILTER
    # =========================================================================
    list_filter = (
        'is_indie',
        ('published_date', admin.DateFieldListFilter),
        'publisher',
    )

    # =========================================================================
    # SEARCH FIELDS
    # =========================================================================
    search_fields = (
        'title',
        'authors',
        'publisher',
        'isbn_13',
    )

    # =========================================================================
    # DEFAULT ORDERING
    # =========================================================================
    ordering = ('title',)

    # =========================================================================
    # LIST PER PAGE
    # =========================================================================
    list_per_page = 20

    # =========================================================================
    # ACTIONS
    # =========================================================================
    actions = ['delete_selected', 'mark_as_indie', 'mark_as_api']

    def mark_as_indie(self, request, queryset):
        updated = queryset.update(is_indie=True)
        self.message_user(request, f'✅ {updated} book(s) marked as indie.')
    mark_as_indie.short_description = "Mark selected as indie books"

    def mark_as_api(self, request, queryset):
        updated = queryset.update(is_indie=False)
        self.message_user(request, f'✅ {updated} book(s) marked as API imports.')
    mark_as_api.short_description = "Mark selected as API imports"

    # =========================================================================
    # CUSTOM QUERYSET FOR SORTING
    # =========================================================================
    def get_queryset(self, request):
        """Annotate queryset with review count and average rating for sorting."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        )

    # =========================================================================
    # CUSTOM METHODS
    # =========================================================================

    def cover_thumbnail(self, obj):
        """Small, consistent cover thumbnails."""
        try:
            if obj.thumbnail_url:
                return format_html(
                    '<img src="{}" style="width: 30px; height: 45px; object-fit: cover; border-radius: 3px;" />',
                    obj.thumbnail_url
                )
        except:
            pass
        return format_html(
            '<div style="width: 30px; height: 45px; background: #f8f9fa; border-radius: 3px;"></div>'
        )
    cover_thumbnail.short_description = 'Cover'
    cover_thumbnail.admin_order_field = 'id'

    def title_short(self, obj):
        """Compact title display with ID."""
        try:
            title = obj.title[:40] + ('...' if len(obj.title) > 40 else '')
        except:
            title = 'Unknown'

        return format_html(
            '<div style="max-width: 200px;">'
            '<strong style="font-size: 13px;">{}</strong><br>'
            '<span style="color: #6c757d; font-size: 10px;">ID: {}</span>'
            '</div>',
            title,
            obj.id
        )
    title_short.short_description = 'Title'
    title_short.admin_order_field = 'title'

    def author_short(self, obj):
        """Compact author display."""
        try:
            authors = obj.get_authors_list()
            if not authors:
                return '—'
            if len(authors) == 1:
                return authors[0][:20] + ('...' if len(authors[0]) > 20 else '')
            return f"{authors[0][:15]} +{len(authors)-1}"
        except:
            return '—'
    author_short.short_description = 'Authors'
    author_short.admin_order_field = 'authors'

    def year(self, obj):
        """Just the year for compactness."""
        try:
            if obj.published_date:
                return obj.published_date.year
        except:
            pass
        return '—'
    year.short_description = 'Year'
    year.admin_order_field = 'published_date'

    def rating_detailed(self, obj):
        """Display rating with stars, average, and review count."""
        try:
            # Get values from annotations or calculate on the fly
            count = getattr(obj, 'review_count', None)
            if count is None:
                count = obj.reviews.count()

            avg = getattr(obj, 'avg_rating', None)
            if avg is None:
                avg = obj.average_rating()

            if count == 0:
                return format_html(
                    '<div style="text-align: center;">'
                    '<span style="color: #6c757d;">—</span><br>'
                    '<span style="color: #999; font-size: 9px;">no reviews</span>'
                    '</div>'
                )

            # Create star rating
            stars = ''
            if avg:
                full_stars = int(avg)
                half_star = (avg - full_stars) >= 0.5
                stars = '★' * full_stars
                if half_star:
                    stars += '½'

            avg_display = f'{avg:.1f}' if avg is not None else '—'

            return format_html(
                '<div style="text-align: center;">'
                '<span style="color: #ffc107; font-size: 14px;">{}</span><br>'
                '<span style="font-weight: 600;">{}</span>'
                '<span style="color: #6c757d; font-size: 9px; display: block;">{} review{}</span>'
                '</div>',
                stars,
                avg_display,
                count,
                's' if count != 1 else ''
            )
        except Exception:
            return format_html('<span style="color: #dc3545;">Error</span>')
    rating_detailed.short_description = 'Rating'
    rating_detailed.admin_order_field = 'avg_rating'

    def indie_badge(self, obj):
        """Compact source badge."""
        try:
            if obj.is_indie:
                return format_html(
                    '<span style="background: #e6f7e6; color: #28a745; padding: 2px 6px; border-radius: 10px; font-size: 10px; white-space: nowrap;">📚 Indie</span>'
                )
            return format_html(
                '<span style="background: #e7f0ff; color: #0066cc; padding: 2px 6px; border-radius: 10px; font-size: 10px; white-space: nowrap;">🌐 API</span>'
            )
        except:
            return format_html('<span>—</span>')
    indie_badge.short_description = 'Source'
    indie_badge.admin_order_field = 'is_indie'

    # =========================================================================
    # CUSTOM ADMIN MEDIA
    # =========================================================================
    class Media:
        pass

    change_list_template = 'admin/books/book/change_list.html'


# =============================================================================
# REGISTRATION
# =============================================================================
admin.site.register(Book, BookAdmin)