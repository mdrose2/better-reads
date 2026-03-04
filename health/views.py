from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
import json

@require_GET
@never_cache
def health_check(request):
    """
    Comprehensive health check endpoint.
    
    Checks:
    - Application is running
    - Database is accessible
    """
    health_status = {
        'status': 'ok',
        'database': 'unknown'
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'error'
        health_status['database'] = 'failed'
        health_status['error'] = str(e)
        return JsonResponse(health_status, status=500)
    
    return JsonResponse(health_status, status=200)