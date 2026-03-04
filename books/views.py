"""
View classes for the books app.

This module contains all view logic for book-related functionality including:
- Listing all books (community library)
- Displaying personal library for logged-in users
- Searching books via Google Books API
- Viewing book details
- Adding books from Google Books API
- Managing indie book submissions
- Admin book management (edit/delete)
"""

import logging
import traceback
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Book
from .utils import GoogleBooksAPI
from .forms import IndieBookForm
from reviews.models import Review

logger = logging.getLogger(__name__)


# ==============================================================================
# LIBRARY VIEWS
# ==============================================================================

class AllBooksListView(ListView):
    """
    Display ALL books in the library (community collection).
    
    Shows every book added by any user or imported from API.
    Visible to all users (authenticated or not).
    
    Template: books/book_list.html
    Context: 
        - 'books': All Book objects, paginated
        - 'page_title': 'Library'
        - 'is_personal_library': False
    Pagination: 20 books per page
    """
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        """Return all books, ordered by most recent."""
        return Book.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add context to indicate this is the community library."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Library'
        context['is_personal_library'] = False
        return context


class MyLibraryView(LoginRequiredMixin, ListView):
    """
    Display books that the current user has interacted with.
    
    Shows:
    - Books the user has added (indie books)
    - Books the user has reviewed
    
    Only visible to authenticated users. Redirects to login if not authenticated.
    
    Template: books/book_list.html
    Context:
        - 'books': Filtered list of Book objects
        - 'page_title': 'My Library'
        - 'is_personal_library': True
    Pagination: 20 books per page
    """
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    login_url = reverse_lazy('users:login')

    def get_queryset(self):
        """
        Return books added or reviewed by the current user.
        
        Combines:
        - Books where user is the added_by (indie books)
        - Books the user has reviewed
        """
        user = self.request.user
        
        # Get books the user has reviewed
        reviewed_book_ids = Review.objects.filter(
            user=user
        ).values_list('book_id', flat=True)
        
        # Get books the user has added (indie books)
        added_book_ids = Book.objects.filter(
            added_by=user
        ).values_list('id', flat=True)
        
        # Combine and get unique books
        book_ids = set(list(reviewed_book_ids) + list(added_book_ids))
        
        return Book.objects.filter(id__in=book_ids).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add context to indicate this is the personal library."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Library'
        context['is_personal_library'] = True
        return context


# ==============================================================================
# BOOK DETAIL VIEW
# ==============================================================================

class BookDetailView(DetailView):
    """
    Display detailed information about a single book.

    Includes book metadata, cover image, description, and all associated reviews.
    Features error handling for non-existent books with user-friendly redirects.

    Template: books/book_detail.html
    Context: 'book' (Book object)
    URL Pattern: /books/<slug:slug>/
    """
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """
        Retrieve the book with error handling.

        Returns None and adds error message if book doesn't exist.
        """
        try:
            return super().get_object(queryset)
        except Exception:
            messages.error(self.request, "Book not found. It may have been deleted.")
            return None

    def get(self, request, *args, **kwargs):
        """Handle GET request with error handling for missing books."""
        book = self.get_object()
        if book is None:
            return redirect('books:list')
        return super().get(request, *args, **kwargs)


# ==============================================================================
# SEARCH VIEWS
# ==============================================================================

class BookSearchView(TemplateView):
    """
    Search for books using the Google Books API.

    Features:
    - Displays search form and results
    - Checks local database for existing books
    - Handles API rate limits and errors with exponential backoff retry logic
    - User-friendly error messages for API issues

    Template: books/book_search.html
    Context:
        - 'query': Current search query
        - 'results': Parsed book data from Google Books API
    """
    template_name = 'books/book_search.html'

    def get_context_data(self, **kwargs):
        """Add search results to context with comprehensive error handling."""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()

        if query:
            logger.info(f"Search initiated for query: {query}")
            
            try:
                api = GoogleBooksAPI()
                logger.info(f"API Key present: {bool(api.api_key)}")
                
                results = api.search_books(query)
                logger.info(f"Raw results type: {type(results)}")
                
                if results is None:
                    logger.error("API returned None")
                    messages.warning(
                        self.request,
                        'The book search service is temporarily unavailable.'
                    )
                    results = []
                
                # Parse results and check against local database
                books_data = []
                for item in results:
                    try:
                        parsed = api.parse_book_data(item)
                        if parsed['google_books_id']:
                            existing = Book.objects.filter(
                                google_books_id=parsed['google_books_id']
                            ).first()
                            parsed['in_database'] = existing is not None
                            parsed['database_id'] = existing.id if existing else None
                        books_data.append(parsed)
                    except Exception as e:
                        logger.error(f"Error parsing book item: {e}")
                        continue
                
                logger.info(f"Successfully parsed {len(books_data)} books")
                context['results'] = books_data

            except Exception as e:
                logger.error(f"Search failed with exception: {str(e)}")
                logger.error(traceback.format_exc())
                messages.error(
                    self.request,
                    'An error occurred while searching. Please try again later.'
                )
                context['results'] = []

            context['query'] = query

        return context


# ==============================================================================
# GOOGLE BOOKS API IMPORT VIEWS
# ==============================================================================

class AddBookFromAPIMixin(CreateView):
    """
    Import a book from Google Books API using its Google Books ID.
    
    For authenticated users: Adds book and redirects to detail page.
    For anonymous users: Adds book, stores book info in session,
    and redirects to login with a next parameter for seamless post-login redirect.
    
    URL Pattern: /books/add/<str:google_books_id>/
    """
    model = Book
    fields = '__all__'
    template_name = 'books/book_add_from_api.html'
    success_url = reverse_lazy('books:list')

    def get(self, request, *args, **kwargs):
        """Handle GET request to import a book from Google Books API."""
        google_books_id = self.kwargs.get('google_books_id')

        # Check if book already exists in database
        existing = Book.objects.filter(google_books_id=google_books_id).first()
        if existing:
            if request.user.is_authenticated:
                messages.info(
                    request,
                    f'📚 "{existing.title}" is already in your library!'
                )
                return redirect('books:detail', slug=existing.slug)
            else:
                # Store book info in session for redirect after login
                request.session['pending_book_slug'] = existing.slug
                request.session['pending_book_title'] = existing.title
                messages.info(
                    request,
                    f'📚 "{existing.title}" is already in our library. '
                    f'Please log in to view it.'
                )
                # Redirect to login with next parameter
                login_url = reverse('users:login')
                next_url = reverse('books:detail', args=[existing.slug])
                return redirect(f"{login_url}?next={next_url}")

        # Fetch book data from API
        api = GoogleBooksAPI()
        book_data = api.get_book_by_id(google_books_id)

        if not book_data:
            messages.error(
                request,
                'Could not fetch book data from Google Books. Please try again.'
            )
            return redirect('books:search')

        # Parse and create book
        parsed_data = api.parse_book_data(book_data)
        book = Book.objects.create(**parsed_data)

        # Custom message based on authentication status
        if request.user.is_authenticated:
            messages.success(
                request,
                f'✅ Successfully added "{book.title}" to your library!'
            )
            return redirect('books:detail', slug=book.slug)
        else:
            # Store book info in session for potential redirect after login
            request.session['pending_book_slug'] = book.slug
            request.session['pending_book_title'] = book.title
            messages.info(
                request,
                f'✨ "{book.title}" has been added to our library! '
                f'Please log in or create an account to view it and write reviews.'
            )
            # Redirect to login with next parameter
            login_url = reverse('users:login')
            next_url = reverse('books:detail', args=[book.slug])
            return redirect(f"{login_url}?next={next_url}")


# ==============================================================================
# ADMIN BOOK MANAGEMENT VIEWS (Superuser Only)
# ==============================================================================

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit book details (superusers only).

    Provides form for editing all book fields.
    Includes error handling for non-existent books.

    Template: books/book_form.html
    URL Pattern: /books/<slug:slug>/edit/
    """
    model = Book
    template_name = 'books/book_form.html'
    fields = [
        'title', 'subtitle', 'authors', 'publisher', 'published_date',
        'description', 'page_count', 'categories', 'cover_image_url',
        'thumbnail_url'
    ]
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        """Only allow superusers to edit books."""
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        """Get the book with error handling for non-existent books."""
        try:
            return super().get_object(queryset)
        except Exception:
            messages.error(
                self.request,
                f"Book with slug '{self.kwargs.get('slug')}' not found."
            )
            return None

    def get(self, request, *args, **kwargs):
        """Handle GET with error handling."""
        book = self.get_object()
        if book is None:
            return redirect('books:list')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Add success message after successful update."""
        messages.success(
            self.request,
            f'<i class="bi bi-check-circle me-2"></i> '
            f'"{self.object.title}" has been updated successfully!'
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to book detail page after successful update."""
        return reverse_lazy('books:detail', kwargs={'slug': self.object.slug})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a book (superusers only).

    Shows confirmation page before deletion.
    Includes error handling for non-existent books.

    Template: books/book_confirm_delete.html
    URL Pattern: /books/<slug:slug>/delete/
    """
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        """Only allow superusers to delete books."""
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        """Get the book with error handling."""
        try:
            return super().get_object(queryset)
        except Exception:
            messages.error(
                self.request,
                "Book not found. It may have been already deleted."
            )
            return None

    def get(self, request, *args, **kwargs):
        """Handle GET with error handling."""
        book = self.get_object()
        if book is None:
            return redirect('books:list')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST with error handling and success message."""
        book = self.get_object()
        if book is None:
            return redirect('books:list')

        # Store title before deletion for success message
        book_title = book.title
        response = super().post(request, *args, **kwargs)
        messages.success(request, f'"{book_title}" has been permanently deleted.')
        return response


# ==============================================================================
# INDIE BOOK MANAGEMENT VIEWS (Community Contributions)
# ==============================================================================

class IndieBookCreateView(LoginRequiredMixin, CreateView):
    """
    Allow any logged-in user to add an indie book to the library.

    Sets is_indie flag and tracks which user added the book.
    Parses comma-separated authors into JSON format.

    Template: books/indie_book_form.html
    URL Pattern: /books/add/indie/
    """
    model = Book
    form_class = IndieBookForm
    template_name = 'books/indie_book_form.html'

    def form_valid(self, form):
        """Set indie book metadata before saving."""
        # Track who added this book
        form.instance.added_by = self.request.user
        form.instance.is_indie = True

        # Parse comma-separated authors into JSON list
        authors_str = form.cleaned_data.get('authors', '')
        if authors_str:
            form.instance.authors = [
                a.strip() for a in authors_str.split(',') if a.strip()
            ]

        messages.success(
            self.request,
            f'✨ "{form.instance.title}" has been added to the library! '
            f'Thank you for contributing.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to new book's detail page after creation."""
        return reverse_lazy('books:detail', kwargs={'slug': self.object.slug})


class IndieBookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allow the user who added the book (or superusers) to edit it.

    Only applies to indie books (is_indie=True).
    Parses comma-separated authors into JSON format.

    Template: books/indie_book_form.html
    URL Pattern: /books/<slug:slug>/edit/indie/
    """
    model = Book
    form_class = IndieBookForm
    template_name = 'books/indie_book_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        """Allow editing if user is superuser OR added the book."""
        book = self.get_object()
        return self.request.user.is_superuser or book.added_by == self.request.user

    def get_queryset(self):
        """Restrict to indie books only."""
        return Book.objects.filter(is_indie=True)

    def form_valid(self, form):
        """Parse authors and add success message."""
        # Parse comma-separated authors into JSON list
        authors_str = form.cleaned_data.get('authors', '')
        if authors_str:
            form.instance.authors = [
                a.strip() for a in authors_str.split(',') if a.strip()
            ]

        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to book detail page after successful update."""
        return reverse_lazy('books:detail', kwargs={'slug': self.object.slug})


class IndieBookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allow the user who added the book (or superusers) to delete it.

    Only applies to indie books (is_indie=True).
    Shows confirmation page before deletion.

    Template: books/indie_book_confirm_delete.html
    URL Pattern: /books/<slug:slug>/delete/indie/
    """
    model = Book
    template_name = 'books/indie_book_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        """Allow deletion if user is superuser OR added the book."""
        book = self.get_object()
        return self.request.user.is_superuser or book.added_by == self.request.user

    def get_queryset(self):
        """Restrict to indie books only."""
        return Book.objects.filter(is_indie=True)

    def delete(self, request, *args, **kwargs):
        """Add success message before deletion."""
        book = self.get_object()
        messages.success(
            request,
            f'"{book.title}" has been removed from the library.'
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        """Redirect to search page after deletion."""
        return reverse_lazy('books:search')