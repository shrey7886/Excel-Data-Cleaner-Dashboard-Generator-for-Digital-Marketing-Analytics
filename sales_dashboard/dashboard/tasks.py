"""
Celery tasks for background data synchronization.
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Client, GoogleAdsCredential, LinkedInAdsCredential, MailchimpCredential,
    ZohoCredential, DemandbaseCredential, GoogleAdsData, LinkedInAdsData,
    MailchimpData, ZohoData, DemandbaseData
)
from api_integrations.google_ads import fetch_google_ads_data
from api_integrations.linkedin_ads import fetch_linkedin_ads_data
from api_integrations.mailchimp import fetch_mailchimp_data
from api_integrations.zoho import fetch_zoho_data
from api_integrations.demandbase import fetch_demandbase_data

logger = logging.getLogger(__name__)

@shared_task
def sync_google_ads_data():
    """Background task to sync Google Ads data for all connected clients."""
    try:
        # Get all clients with Google Ads credentials
        clients = Client.objects.filter(google_ads_credentials__isnull=False).distinct()
        
        for client in clients:
            try:
                logger.info(f"Syncing Google Ads data for client: {client.company}")
                
                # Fetch data from Google Ads API
                df = fetch_google_ads_data()
                
                # Save to database
                GoogleAdsData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                
                logger.info(f"Successfully synced Google Ads data for client: {client.company}")
                
            except Exception as e:
                logger.error(f"Failed to sync Google Ads data for client {client.company}: {str(e)}")
                continue
        
        return f"Synced Google Ads data for {clients.count()} clients"
        
    except Exception as e:
        logger.error(f"Google Ads sync task failed: {str(e)}")
        raise

@shared_task
def sync_linkedin_ads_data():
    """Background task to sync LinkedIn Ads data for all connected clients."""
    try:
        # Get all clients with LinkedIn Ads credentials
        clients = Client.objects.filter(linkedin_ads_credentials__isnull=False).distinct()
        
        for client in clients:
            try:
                logger.info(f"Syncing LinkedIn Ads data for client: {client.company}")
                
                # Fetch data from LinkedIn Ads API
                df = fetch_linkedin_ads_data()
                
                # Save to database
                LinkedInAdsData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                
                logger.info(f"Successfully synced LinkedIn Ads data for client: {client.company}")
                
            except Exception as e:
                logger.error(f"Failed to sync LinkedIn Ads data for client {client.company}: {str(e)}")
                continue
        
        return f"Synced LinkedIn Ads data for {clients.count()} clients"
        
    except Exception as e:
        logger.error(f"LinkedIn Ads sync task failed: {str(e)}")
        raise

@shared_task
def sync_mailchimp_data():
    """Background task to sync Mailchimp data for all connected clients."""
    try:
        # Get all clients with Mailchimp credentials
        clients = Client.objects.filter(mailchimp_credentials__isnull=False).distinct()
        
        for client in clients:
            try:
                logger.info(f"Syncing Mailchimp data for client: {client.company}")
                
                # Fetch data from Mailchimp API
                df = fetch_mailchimp_data()
                
                # Save to database
                MailchimpData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                
                logger.info(f"Successfully synced Mailchimp data for client: {client.company}")
                
            except Exception as e:
                logger.error(f"Failed to sync Mailchimp data for client {client.company}: {str(e)}")
                continue
        
        return f"Synced Mailchimp data for {clients.count()} clients"
        
    except Exception as e:
        logger.error(f"Mailchimp sync task failed: {str(e)}")
        raise

@shared_task
def sync_zoho_data():
    """Background task to sync Zoho data for all connected clients."""
    try:
        # Get all clients with Zoho credentials
        clients = Client.objects.filter(zoho_credentials__isnull=False).distinct()
        
        for client in clients:
            try:
                logger.info(f"Syncing Zoho data for client: {client.company}")
                
                # Fetch data from Zoho API
                df = fetch_zoho_data()
                
                # Save to database
                ZohoData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                
                logger.info(f"Successfully synced Zoho data for client: {client.company}")
                
            except Exception as e:
                logger.error(f"Failed to sync Zoho data for client {client.company}: {str(e)}")
                continue
        
        return f"Synced Zoho data for {clients.count()} clients"
        
    except Exception as e:
        logger.error(f"Zoho sync task failed: {str(e)}")
        raise

@shared_task
def sync_demandbase_data():
    """Background task to sync Demandbase data for all connected clients."""
    try:
        # Get all clients with Demandbase credentials
        clients = Client.objects.filter(demandbase_credentials__isnull=False).distinct()
        
        for client in clients:
            try:
                logger.info(f"Syncing Demandbase data for client: {client.company}")
                
                # Fetch data from Demandbase API
                df = fetch_demandbase_data()
                
                # Save to database
                DemandbaseData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                
                logger.info(f"Successfully synced Demandbase data for client: {client.company}")
                
            except Exception as e:
                logger.error(f"Failed to sync Demandbase data for client {client.company}: {str(e)}")
                continue
        
        return f"Synced Demandbase data for {clients.count()} clients"
        
    except Exception as e:
        logger.error(f"Demandbase sync task failed: {str(e)}")
        raise

@shared_task
def sync_all_platform_data():
    """Background task to sync data from all platforms for all connected clients."""
    try:
        logger.info("Starting background sync for all platforms")
        
        # Run all sync tasks
        results = []
        
        # Google Ads
        try:
            google_result = sync_google_ads_data.delay()
            results.append(f"Google Ads: {google_result.get()}")
        except Exception as e:
            results.append(f"Google Ads: Failed - {str(e)}")
        
        # LinkedIn Ads
        try:
            linkedin_result = sync_linkedin_ads_data.delay()
            results.append(f"LinkedIn Ads: {linkedin_result.get()}")
        except Exception as e:
            results.append(f"LinkedIn Ads: Failed - {str(e)}")
        
        # Mailchimp
        try:
            mailchimp_result = sync_mailchimp_data.delay()
            results.append(f"Mailchimp: {mailchimp_result.get()}")
        except Exception as e:
            results.append(f"Mailchimp: Failed - {str(e)}")
        
        # Zoho
        try:
            zoho_result = sync_zoho_data.delay()
            results.append(f"Zoho: {zoho_result.get()}")
        except Exception as e:
            results.append(f"Zoho: Failed - {str(e)}")
        
        # Demandbase
        try:
            demandbase_result = sync_demandbase_data.delay()
            results.append(f"Demandbase: {demandbase_result.get()}")
        except Exception as e:
            results.append(f"Demandbase: Failed - {str(e)}")
        
        logger.info(f"Background sync completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Background sync task failed: {str(e)}")
        raise

@shared_task
def cleanup_old_data():
    """Background task to cleanup old data (keep last 30 days)."""
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Cleanup old data from all platforms
        platforms = [
            (GoogleAdsData, 'Google Ads'),
            (LinkedInAdsData, 'LinkedIn Ads'),
            (MailchimpData, 'Mailchimp'),
            (ZohoData, 'Zoho'),
            (DemandbaseData, 'Demandbase')
        ]
        
        total_deleted = 0
        for model, name in platforms:
            deleted_count, _ = model.objects.filter(fetched_at__lt=cutoff_date).delete()
            total_deleted += deleted_count
            logger.info(f"Deleted {deleted_count} old {name} records")
        
        logger.info(f"Cleanup completed: {total_deleted} old records deleted")
        return f"Deleted {total_deleted} old records"
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise

@shared_task
def refresh_expired_tokens():
    """Background task to refresh expired OAuth tokens."""
    try:
        from .views import refresh_google_token, refresh_linkedin_token
        
        # Refresh Google Ads tokens
        google_credentials = GoogleAdsCredential.objects.filter(
            token_expires_at__lt=timezone.now()
        )
        
        for cred in google_credentials:
            try:
                refresh_google_token(cred)
                logger.info(f"Refreshed Google Ads token for client: {cred.client.company}")
            except Exception as e:
                logger.error(f"Failed to refresh Google Ads token for client {cred.client.company}: {str(e)}")
        
        # Refresh LinkedIn Ads tokens
        linkedin_credentials = LinkedInAdsCredential.objects.filter(
            token_expires_at__lt=timezone.now()
        )
        
        for cred in linkedin_credentials:
            try:
                refresh_linkedin_token(cred)
                logger.info(f"Refreshed LinkedIn Ads token for client: {cred.client.company}")
            except Exception as e:
                logger.error(f"Failed to refresh LinkedIn Ads token for client {cred.client.company}: {str(e)}")
        
        return f"Refreshed {google_credentials.count() + linkedin_credentials.count()} tokens"
        
    except Exception as e:
        logger.error(f"Token refresh task failed: {str(e)}")
        raise 