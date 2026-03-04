# reviews/migrations/0003_add_review_slugs_combined.py
from django.db import migrations, models
from django.utils.text import slugify
from django.utils import timezone

def generate_review_slugs(apps, schema_editor):
    Review = apps.get_model('reviews', 'Review')
    for review in Review.objects.all():
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        base_slug = slugify(f"{review.user.username}-review-of-{review.book.title}")[:70]
        slug = f"{base_slug}-{timestamp}"
        
        # Ensure uniqueness
        counter = 1
        original_slug = slug
        while Review.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        review.slug = slug
        review.save()

class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0002_alter_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, null=True,
                                   help_text="URL-friendly version of the review"),
        ),
        migrations.RunPython(generate_review_slugs, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='review',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True,
                                   help_text="URL-friendly version of the review"),
        ),
    ]