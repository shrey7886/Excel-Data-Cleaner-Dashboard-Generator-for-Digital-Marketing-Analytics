"""
OAuth Configuration for Google Ads and LinkedIn Ads

This file contains instructions for setting up OAuth applications for Google Ads and LinkedIn Ads.

GOOGLE ADS OAUTH SETUP:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the Google Ads API
4. Go to "Credentials" and create OAuth 2.0 Client ID
5. Set authorized redirect URI to: http://localhost:8000/dashboard/oauth/google/callback/
6. Copy Client ID and Client Secret to environment variables

LINKEDIN ADS OAUTH SETUP:
1. Go to LinkedIn Developers (https://www.linkedin.com/developers/)
2. Create a new app
3. Add OAuth 2.0 redirect URL: http://localhost:8000/dashboard/oauth/linkedin/callback/
4. Request access to Marketing Developer Platform
5. Copy Client ID and Client Secret to environment variables

ENVIRONMENT VARIABLES:
Set these in your .env file or environment:

GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/dashboard/oauth/google/callback/

LINKEDIN_OAUTH_CLIENT_ID=your-linkedin-client-id
LINKEDIN_OAUTH_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_OAUTH_REDIRECT_URI=http://localhost:8000/dashboard/oauth/linkedin/callback/

For production, update the redirect URIs to your domain.
"""

import os
from django.conf import settings

def get_oauth_config():
    """Get OAuth configuration from environment variables."""
    return {
        'google': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'your-google-client-id'),
            'client_secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'your-google-client-secret'),
            'redirect_uri': os.environ.get('GOOGLE_OAUTH_REDIRECT_URI', 'http://localhost:8000/dashboard/oauth/google/callback/'),
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scope': 'https://www.googleapis.com/auth/adwords'
        },
        'linkedin': {
            'client_id': os.environ.get('LINKEDIN_OAUTH_CLIENT_ID', 'your-linkedin-client-id'),
            'client_secret': os.environ.get('LINKEDIN_OAUTH_CLIENT_SECRET', 'your-linkedin-client-secret'),
            'redirect_uri': os.environ.get('LINKEDIN_OAUTH_REDIRECT_URI', 'http://localhost:8000/dashboard/oauth/linkedin/callback/'),
            'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
            'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
            'scope': 'r_ads r_ads_reporting'
        }
    }

def is_oauth_configured():
    """Check if OAuth is properly configured."""
    config = get_oauth_config()
    google_configured = (config['google']['client_id'] != 'your-google-client-id' and 
                        config['google']['client_secret'] != 'your-google-client-secret')
    linkedin_configured = (config['linkedin']['client_id'] != 'your-linkedin-client-id' and 
                          config['linkedin']['client_secret'] != 'your-linkedin-client-secret')
    
    return {
        'google': google_configured,
        'linkedin': linkedin_configured,
        'all_configured': google_configured and linkedin_configured
    } 