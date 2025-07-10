# Background Sync Setup Guide

This guide explains how to set up background data synchronization using Celery for the Django SaaS marketing analytics platform.

## Overview

The platform uses Celery for background tasks to:
- Sync data from all connected platforms every 4-6 hours
- Clean up old data daily
- Refresh expired OAuth tokens hourly
- Provide real-time data updates without manual intervention

## Prerequisites

1. **Redis Server** (required for Celery broker)
2. **Python packages**: celery, redis, django-celery-beat

## Installation

### 1. Install Required Packages

```bash
pip install celery redis django-celery-beat
```

### 2. Add to Django Settings

Add these apps to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_celery_beat',
]
```

### 3. Configure Celery Settings

The following settings are already configured in `settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

## Running Background Tasks

### 1. Start Redis Server

```bash
# On Windows
redis-server

# On macOS/Linux
sudo service redis start
# or
redis-server
```

### 2. Start Celery Worker

```bash
# From the sales_dashboard directory
celery -A sales_dashboard worker --loglevel=info
```

### 3. Start Celery Beat (Scheduler)

```bash
# From the sales_dashboard directory
celery -A sales_dashboard beat --loglevel=info
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

## Scheduled Tasks

The following tasks are automatically scheduled:

### Data Sync Tasks
- **All Platforms**: Every 6 hours (00:00, 06:00, 12:00, 18:00)
- **Individual Platforms**: Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
  - Google Ads
  - LinkedIn Ads
  - Mailchimp
  - Zoho
  - Demandbase

### Maintenance Tasks
- **Cleanup Old Data**: Daily at 2:00 AM (keeps last 30 days)
- **Refresh Expired Tokens**: Every hour

## Manual Task Execution

### Using Django Management Command

```bash
# Sync all platforms
python manage.py start_background_syncs

# Sync specific platform
python manage.py start_background_syncs --platform google_ads

# Run cleanup
python manage.py start_background_syncs --cleanup

# Refresh tokens
python manage.py start_background_syncs --refresh-tokens
```

### Using Celery Directly

```bash
# From Python shell or Django shell
from dashboard.tasks import sync_all_platform_data
result = sync_all_platform_data.delay()
print(f"Task ID: {result.id}")
```

## Monitoring Tasks

### 1. Check Task Status

```python
from celery.result import AsyncResult

# Get task result
result = AsyncResult('task-id-here')
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### 2. View Task Logs

Celery workers log all task executions. Check the console output or log files for:
- Task start/completion
- Error messages
- Performance metrics

### 3. Monitor Redis

```bash
# Connect to Redis CLI
redis-cli

# List all keys
KEYS *

# Monitor Redis operations
MONITOR
```

## Production Deployment

### 1. Environment Variables

Set these in your production environment:

```bash
CELERY_BROKER_URL=redis://your-redis-server:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-server:6379/0
```

### 2. Process Management

Use Supervisor or systemd to manage Celery processes:

**Supervisor Configuration** (`/etc/supervisor/conf.d/celery.conf`):

```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A sales_dashboard worker --loglevel=info
directory=/path/to/project
user=celery
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600

[program:celery-beat]
command=/path/to/venv/bin/celery -A sales_dashboard beat --loglevel=info
directory=/path/to/project
user=celery
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
```

### 3. Logging

Configure logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/celery/django.log',
        },
    },
    'loggers': {
        'dashboard.tasks': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running
   - Check CELERY_BROKER_URL configuration
   - Verify network connectivity

2. **Task Not Executing**
   - Check Celery worker is running
   - Verify Celery beat scheduler is running
   - Check task imports in `tasks.py`

3. **OAuth Token Refresh Failures**
   - Verify OAuth credentials are valid
   - Check token expiration times
   - Review API rate limits

### Debug Commands

```bash
# Check Celery status
celery -A sales_dashboard inspect active

# List scheduled tasks
celery -A sales_dashboard inspect scheduled

# Check worker status
celery -A sales_dashboard inspect stats
```

## Performance Optimization

1. **Worker Processes**: Adjust based on CPU cores
2. **Redis Memory**: Monitor memory usage
3. **Task Timeouts**: Set appropriate timeouts for long-running tasks
4. **Database Connections**: Use connection pooling for database operations

## Security Considerations

1. **Redis Security**: Configure Redis authentication
2. **Task Serialization**: Use JSON serializer (already configured)
3. **Environment Variables**: Store sensitive data in environment variables
4. **Network Security**: Use SSL/TLS for Redis connections in production 