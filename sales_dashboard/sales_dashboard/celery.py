"""
Celery configuration for sales_dashboard project.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_dashboard.settings_production')

app = Celery('sales_dashboard')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule Configuration
app.conf.beat_schedule = {
    # Sync all platform data every 6 hours
    'sync-all-platform-data': {
        'task': 'dashboard.tasks.sync_all_platform_data',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    
    # Individual platform syncs (every 4 hours)
    'sync-google-ads-data': {
        'task': 'dashboard.tasks.sync_google_ads_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    'sync-linkedin-ads-data': {
        'task': 'dashboard.tasks.sync_linkedin_ads_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    'sync-mailchimp-data': {
        'task': 'dashboard.tasks.sync_mailchimp_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    'sync-zoho-data': {
        'task': 'dashboard.tasks.sync_zoho_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    'sync-demandbase-data': {
        'task': 'dashboard.tasks.sync_demandbase_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    
    # Cleanup old data daily at 2 AM
    'cleanup-old-data': {
        'task': 'dashboard.tasks.cleanup_old_data',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    
    # Refresh expired tokens every hour
    'refresh-expired-tokens': {
        'task': 'dashboard.tasks.refresh_expired_tokens',
        'schedule': crontab(minute=0, hour='*'),  # Every hour
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 