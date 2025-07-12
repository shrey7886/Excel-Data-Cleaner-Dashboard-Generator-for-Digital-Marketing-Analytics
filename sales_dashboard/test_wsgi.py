#!/usr/bin/env python3
"""
WSGI Test Script for Targetorate
This script tests the WSGI configuration and can be used for debugging.
"""

import os
import sys
from pathlib import Path

# Add the project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def test_wsgi_configuration():
    """Test the WSGI configuration."""
    print("Testing WSGI configuration...")
    
    # Test environment setup
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")
    
    # Test Django settings
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings')
        from django.conf import settings
        print(f"✅ Django settings loaded successfully")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   DATABASES: {list(settings.DATABASES.keys())}")
    except Exception as e:
        print(f"❌ Django settings error: {e}")
        return False
    
    # Test WSGI application
    try:
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        print("✅ WSGI application created successfully")
    except Exception as e:
        print(f"❌ WSGI application error: {e}")
        return False
    
    # Test health check
    try:
        from sales_dashboard.wsgi import health_check
        print("✅ Health check function available")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    print("✅ All WSGI tests passed!")
    return True

def test_production_settings():
    """Test production settings configuration."""
    print("\nTesting production settings...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings_production')
        from django.conf import settings
        print(f"✅ Production settings loaded successfully")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}")
        print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    except Exception as e:
        print(f"❌ Production settings error: {e}")
        return False
    
    print("✅ Production settings test passed!")
    return True

def test_database_connection():
    """Test database connection."""
    print("\nTesting database connection...")
    
    try:
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Database connection successful: {result}")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    print("✅ Database connection test passed!")
    return True

def main():
    """Main test function."""
    print("🚀 Targetorate WSGI Configuration Test")
    print("=" * 50)
    
    # Test basic WSGI configuration
    if not test_wsgi_configuration():
        print("❌ WSGI configuration test failed!")
        return 1
    
    # Test production settings
    if not test_production_settings():
        print("❌ Production settings test failed!")
        return 1
    
    # Test database connection
    if not test_database_connection():
        print("❌ Database connection test failed!")
        return 1
    
    print("\n🎉 All tests passed! WSGI configuration is ready.")
    print("\nYou can now run:")
    print("  python manage.py runserver")
    print("  gunicorn sales_dashboard.wsgi:application")
    print("  docker-compose up")
    
    return 0

if __name__ == "__main__":
    exit(main()) 