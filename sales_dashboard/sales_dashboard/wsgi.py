"""
WSGI config for sales_dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module based on environment
DJANGO_SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)

# Import Django and configure settings
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except ImportError as e:
    print(f"Error importing Django: {e}")
    print("Please ensure Django is installed and the settings module is correct.")
    raise

# Add health check endpoint for container orchestration
def health_check(environ, start_response):
    """Simple health check endpoint."""
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [b'OK']

# WSGI application with health check
def wsgi_application(environ, start_response):
    """WSGI application with health check support."""
    path = environ.get('PATH_INFO', '')
    
    # Health check endpoint
    if path == '/health/':
        return health_check(environ, start_response)
    
    # Regular Django application
    return application(environ, start_response)

# For compatibility with different deployment methods
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, wsgi_application)
    print("Serving on port 8000...")
    httpd.serve_forever()
