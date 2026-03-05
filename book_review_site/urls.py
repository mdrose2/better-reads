"""
URL configuration for book_review_site project.

The `urlpatterns` list routes URLs to views. For more information see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve 

from health.views import health_check

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Site pages
    path('', include('pages.urls')),      # Home page
    
    # App URLs
    path('books/', include('books.urls')),    # Book management
    path('reviews/', include('reviews.urls')), # Review management
    path('users/', include('users.urls')),     # User authentication
    
    # Health checks
    path('health/', health_check, name='health-check'),
    path('checkpointpls', health_check, name='render-health-check'),
]

# Serve media files
if settings.DEBUG:
    # Development - use Django's static helper
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production - use explicit serve view
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]