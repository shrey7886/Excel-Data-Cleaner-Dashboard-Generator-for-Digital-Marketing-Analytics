"""
ASGI config for sales_dashboard project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
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
    from django.core.asgi import get_asgi_application
    application = get_asgi_application()
except ImportError as e:
    print(f"Error importing Django: {e}")
    print("Please ensure Django is installed and the settings module is correct.")
    raise

# For compatibility with different deployment methods
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
