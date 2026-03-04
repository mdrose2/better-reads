"""
Management command to add URL-friendly slugs to existing books.

This command populates the slug field for any books that were created
before the slug functionality was added. It's designed to be run once
after the slug migration, but can safely be run multiple times as it
only processes books without slugs.

Usage:
    python manage.py add_slugs
"""

from django.core.management.base import BaseCommand
from books.models import Book

class Command(BaseCommand):
    """Add URL-friendly slugs to existing books."""
    
    help = 'Generate slugs for books missing them'

    def handle(self, *args, **options):
        """
        Find all books without slugs and generate one for each.
        
        The book's save() method handles the actual slug generation,
        ensuring each slug is unique and URL-friendly.
        """
        # Get all books that need slugs
        books_without_slugs = Book.objects.filter(slug__isnull=True)
        count = books_without_slugs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All books already have slugs!'))
            return
        
        self.stdout.write(f'Found {count} book(s) without slugs...')
        
        # Generate slugs for each book
        for book in books_without_slugs:
            book.save()  # Triggers automatic slug creation
            self.stdout.write(f'  ✓ Added slug to: {book.title}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully added slugs to {count} book(s)')
        )