import os

# OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'your-google-client-id')
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_OAUTH_REDIRECT_URI = os.environ.get(
    'GOOGLE_OAUTH_REDIRECT_URI',
    'http://localhost:8000/dashboard/oauth/google/callback/'
)

LINKEDIN_OAUTH_CLIENT_ID = os.environ.get('LINKEDIN_OAUTH_CLIENT_ID', 'your-linkedin-client-id')
LINKEDIN_OAUTH_CLIENT_SECRET = os.environ.get('LINKEDIN_OAUTH_CLIENT_SECRET', 'your-linkedin-client-secret')
LINKEDIN_OAUTH_REDIRECT_URI = os.environ.get(
    'LINKEDIN_OAUTH_REDIRECT_URI',
    'http://localhost:8000/dashboard/oauth/linkedin/callback/'
)

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler' 

