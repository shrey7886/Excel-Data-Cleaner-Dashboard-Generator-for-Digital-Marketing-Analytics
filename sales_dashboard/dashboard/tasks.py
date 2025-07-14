"""
Celery tasks for background data synchronization.
"""

import logging
from celery import shared_task
from django.utils import timezone
from .models import (
    Client, GoogleAdsCredential, LinkedInAdsCredential, ZohoCredential,
    GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, 
    DemandbaseData, UnifiedClientData
)
from api_integrations.google_ads import fetch_google_ads_data
from api_integrations.linkedin_ads import fetch_linkedin_ads_data
from api_integrations.mailchimp import fetch_mailchimp_data
from api_integrations.zoho import fetch_zoho_data
from api_integrations.demandbase import fetch_demandbase_data
from dashboard.rag_pipeline import update_rag_index_from_db


logger = logging.getLogger(__name__)


def aggregate_unified_data_for_client(client):
    """Aggregate latest data from all tools and update UnifiedClientData summary for the client."""
    import datetime
    tool_models = [
        GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData
    ]
    all_data = []
    platforms = []
    date_start, date_end = None, None
    total_records = 0
    for model in tool_models:
        tool_data = model.objects.filter(client=client).order_by('-fetched_at')
        if tool_data.exists():
            platforms.append(model.__name__.replace('Data', ''))
            for entry in tool_data:
                entry_data = (
                    entry.data if isinstance(entry.data, list)
                    else [entry.data] if isinstance(entry.data, dict)
                    else []
                )
                all_data.extend(entry_data)
                for record in entry_data:
                    date_val = record.get('date') or record.get('Date')
                    if date_val:
                        try:
                            d = datetime.datetime.strptime(
                                str(date_val), '%Y-%m-%d'
                            ).date()
                            if not date_start or d < date_start:
                                date_start = d
                            if not date_end or d > date_end:
                                date_end = d
                        except Exception:
                            continue
    total_records = len(all_data)
    kpis = {'impressions': 0, 'clicks': 0, 'spend': 0, 'revenue': 0}
    for record in all_data:
        for k in kpis:
            try:
                kpis[k] += float(record.get(k, 0) or 0)
            except Exception:
                continue
    UnifiedClientData.objects.update_or_create(
        client=client,
        defaults={
            'status': 'synced',
            'total_records': total_records,
            'date_range_start': date_start,
            'date_range_end': date_end,
            'platforms_included': platforms,
            'data_summary': kpis,
            'processing_started_at': timezone.now(),
            'processing_completed_at': timezone.now(),
        }
    )


@shared_task
def sync_google_ads_data():
    """Background task to sync Google Ads data for all connected clients."""
    try:
        # Get all clients with Google Ads credentials
        clients = Client.objects.filter(
            google_ads_credentials__isnull=False
        ).distinct()

        for client in clients:
            try:
                logger.info(
                    f"Syncing Google Ads data for client: {client.company}"
                )

                # Fetch data from Google Ads API
                df = fetch_google_ads_data(client)

                # Save to database
                GoogleAdsData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                # AGGREGATE unified data
                aggregate_unified_data_for_client(client)

                logger.info(
                    f"Successfully synced Google Ads data for client: {client.company}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to sync Google Ads data for client {client.company}: {str(e)}"
                )
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
        clients = Client.objects.filter(
            linkedin_ads_credentials__isnull=False
        ).distinct()

        for client in clients:
            try:
                logger.info(
                    f"Syncing LinkedIn Ads data for client: {client.company}"
                )

                # Fetch data from LinkedIn Ads API
                df = fetch_linkedin_ads_data(client)

                # Save to database
                LinkedInAdsData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                aggregate_unified_data_for_client(client)

                logger.info(
                    f"Successfully synced LinkedIn Ads data for client: {client.company}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to sync LinkedIn Ads data for client {client.company}: {str(e)}"
                )
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
        clients = Client.objects.filter(
            mailchimp_credentials__isnull=False
        ).distinct()

        for client in clients:
            try:
                logger.info(
                    f"Syncing Mailchimp data for client: {client.company}"
                )

                # Fetch data from Mailchimp API
                df = fetch_mailchimp_data(client)

                # Save to database
                MailchimpData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                aggregate_unified_data_for_client(client)

                logger.info(
                    f"Successfully synced Mailchimp data for client: {client.company}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to sync Mailchimp data for client {client.company}: {str(e)}"
                )
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
        clients = Client.objects.filter(
            zoho_credentials__isnull=False
        ).distinct()

        for client in clients:
            try:
                logger.info(f"Syncing Zoho data for client: {client.company}")

                # Fetch data from Zoho API
                df = fetch_zoho_data(client)

                # Save to database
                ZohoData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                aggregate_unified_data_for_client(client)

                logger.info(
                    f"Successfully synced Zoho data for client: {client.company}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to sync Zoho data for client {client.company}: {str(e)}"
                )
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
        clients = Client.objects.filter(
            demandbase_credentials__isnull=False
        ).distinct()

        for client in clients:
            try:
                logger.info(
                    f"Syncing Demandbase data for client: {client.company}"
                )

                # Fetch data from Demandbase API
                df = fetch_demandbase_data(client)

                # Save to database
                DemandbaseData.objects.create(
                    client=client,
                    data=df.to_dict(orient='records'),
                    fetched_at=timezone.now()
                )
                aggregate_unified_data_for_client(client)

                logger.info(
                    f"Successfully synced Demandbase data for client: {client.company}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to sync Demandbase data for client {client.company}: {str(e)}"
                )
                continue

        return f"Synced Demandbase data for {clients.count()} clients"

    except Exception as e:
        logger.error(f"Demandbase sync task failed: {str(e)}")
        raise


@shared_task
def sync_all_platform_data():
    """Background task to sync data from all platforms for all connected clients."""
    try:
        logger.info("Starting sync of all platform data")

        # Sync each platform
        google_ads_result = sync_google_ads_data.delay()
        linkedin_ads_result = sync_linkedin_ads_data.delay()
        mailchimp_result = sync_mailchimp_data.delay()
        zoho_result = sync_zoho_data.delay()
        demandbase_result = sync_demandbase_data.delay()

        # Wait for all tasks to complete
        results = [
            google_ads_result.get(),
            linkedin_ads_result.get(),
            mailchimp_result.get(),
            zoho_result.get(),
            demandbase_result.get()
        ]

        logger.info("Completed sync of all platform data")
        return {
            'google_ads': results[0],
            'linkedin_ads': results[1],
            'mailchimp': results[2],
            'zoho': results[3],
            'demandbase': results[4]
        }

    except Exception as e:
        logger.error(f"All platform sync task failed: {str(e)}")
        raise


@shared_task
def cleanup_old_data():
    """Background task to clean up old data records."""
    try:
        from datetime import timedelta

        # Delete data older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)

        # Clean up old data from all platforms
        platforms = [
            GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData
        ]

        total_deleted = 0
        for platform in platforms:
            deleted_count = platform.objects.filter(
                fetched_at__lt=cutoff_date
            ).delete()[0]
            total_deleted += deleted_count
            logger.info(f"Deleted {deleted_count} old {platform.__name__} records")

        logger.info(f"Cleanup completed. Total deleted: {total_deleted}")
        return f"Deleted {total_deleted} old records"

    except Exception as e:
        logger.error(f"Data cleanup task failed: {str(e)}")
        raise


@shared_task
def refresh_expired_tokens():
    """Background task to refresh expired OAuth tokens."""
    try:
        from datetime import timedelta

        # Check for tokens expiring in the next 7 days
        warning_date = timezone.now() + timedelta(days=7)

        # Check Google Ads tokens
        google_ads_creds = GoogleAdsCredential.objects.filter(
            expires_at__lt=warning_date
        )
        for cred in google_ads_creds:
            logger.warning(
                f"Google Ads token for client {cred.client.company} expires soon"
            )

        # Check LinkedIn Ads tokens
        linkedin_ads_creds = LinkedInAdsCredential.objects.filter(
            expires_at__lt=warning_date
        )
        for cred in linkedin_ads_creds:
            logger.warning(
                f"LinkedIn Ads token for client {cred.client.company} expires soon"
            )

        # Check Zoho tokens
        zoho_creds = ZohoCredential.objects.filter(
            expires_at__lt=warning_date
        )
        for cred in zoho_creds:
            logger.warning(
                f"Zoho token for client {cred.client.company} expires soon"
            )

        total_warnings = (
            google_ads_creds.count() + linkedin_ads_creds.count() + zoho_creds.count()
        )

        logger.info(f"Token refresh check completed. {total_warnings} tokens need attention")
        return f"Checked {total_warnings} expiring tokens"

    except Exception as e:
        logger.error(f"Token refresh task failed: {str(e)}")
        raise 


@shared_task
def update_rag_index_task():
    """Background task to update the RAG FAISS index from marketing data."""
    update_rag_index_from_db()
    return "RAG index updated successfully." 



