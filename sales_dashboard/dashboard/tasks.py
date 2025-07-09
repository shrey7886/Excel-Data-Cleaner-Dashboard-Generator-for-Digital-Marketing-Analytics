"""
Celery tasks for background processing.
"""

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Campaign, CampaignReport, Client, GoogleAdsCredential, MailchimpCredential, LinkedInAdsCredential, ZohoCredential
from datetime import datetime, timedelta
import pandas as pd
from django_q.tasks import schedule
from api_integrations.google_ads import fetch_google_ads_data
from api_integrations.mailchimp import fetch_mailchimp_data
from api_integrations.linkedin_ads import fetch_linkedin_ads_data
from api_integrations.zoho import fetch_zoho_data
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def generate_weekly_report(client_id):
    """Generate weekly report for a client."""
    try:
        client = Client.objects.get(id=client_id)
        campaigns = Campaign.objects.filter(client=client)
        
        # Generate report data
        report_data = {
            'client': client,
            'campaigns': campaigns,
            'total_spend': sum(campaign.budget for campaign in campaigns),
            'total_revenue': sum(campaign.revenue for campaign in campaigns),
            'roas': sum(campaign.revenue for campaign in campaigns) / sum(campaign.budget for campaign in campaigns) if sum(campaign.budget for campaign in campaigns) > 0 else 0,
        }
        
        # Create report
        report = CampaignReport.objects.create(
            client=client,
            report_type='weekly',
            title=f"Weekly Report - {client.name}",
            content=f"Weekly performance report for {client.name}",
            kpi_data=report_data,
            generated_at=datetime.now()
        )
        
        logger.info(f"Weekly report generated for client {client.name}")
        return f"Report {report.id} generated successfully"
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        raise

@shared_task
def send_report_email(report_id):
    """Send report via email."""
    try:
        report = CampaignReport.objects.get(id=report_id)
        client = report.client
        
        subject = f"Sales Dashboard Report - {report.title}"
        message = f"""
        Hello {client.name},
        
        Your report "{report.title}" has been generated and is ready for review.
        
        Report Details:
        - Type: {report.report_type}
        - Generated: {report.generated_at}
        
        You can view the full report in your dashboard.
        
        Best regards,
        Sales Dashboard Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            fail_silently=False,
        )
        
        logger.info(f"Report email sent to {client.email}")
        return f"Email sent to {client.email}"
        
    except Exception as e:
        logger.error(f"Error sending report email: {str(e)}")
        raise

@shared_task
def process_campaign_data(campaign_id):
    """Process and analyze campaign data."""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # Simulate data processing
        # In a real application, this would involve:
        # - Fetching data from APIs
        # - Running ML models
        # - Updating campaign metrics
        
        campaign.status = 'active'
        campaign.save()
        
        logger.info(f"Campaign data processed for {campaign.name}")
        return f"Campaign {campaign.name} processed successfully"
        
    except Exception as e:
        logger.error(f"Error processing campaign data: {str(e)}")
        raise

@shared_task
def cleanup_old_reports():
    """Clean up reports older than 90 days."""
    try:
        cutoff_date = datetime.now() - timedelta(days=90)
        old_reports = CampaignReport.objects.filter(generated_at__lt=cutoff_date)
        count = old_reports.count()
        old_reports.delete()
        
        logger.info(f"Cleaned up {count} old reports")
        return f"{count} old reports cleaned up"
        
    except Exception as e:
        logger.error(f"Error cleaning up old reports: {str(e)}")
        raise

@shared_task
def update_campaign_metrics():
    """Update campaign metrics for all active campaigns."""
    try:
        active_campaigns = Campaign.objects.filter(status='active')
        updated_count = 0
        
        for campaign in active_campaigns:
            # Simulate metric updates
            # In a real application, this would fetch real-time data
            campaign.impressions += 1000
            campaign.clicks += 50
            campaign.conversions += 5
            campaign.save()
            updated_count += 1
        
        logger.info(f"Updated metrics for {updated_count} campaigns")
        return f"{updated_count} campaigns updated"
        
    except Exception as e:
        logger.error(f"Error updating campaign metrics: {str(e)}")
        raise

@shared_task
def generate_monthly_insights():
    """Generate monthly insights for all clients."""
    try:
        clients = Client.objects.all()
        insights_generated = 0
        
        for client in clients:
            campaigns = Campaign.objects.filter(client=client)
            
            if campaigns.exists():
                # Calculate insights
                total_spend = sum(c.budget for c in campaigns)
                total_revenue = sum(c.revenue for c in campaigns)
                avg_ctr = sum(c.ctr for c in campaigns) / len(campaigns) if campaigns else 0
                
                insight_data = {
                    'total_spend': total_spend,
                    'total_revenue': total_revenue,
                    'roas': total_revenue / total_spend if total_spend > 0 else 0,
                    'avg_ctr': avg_ctr,
                    'campaign_count': len(campaigns),
                }
                
                # Create insight report
                CampaignReport.objects.create(
                    client=client,
                    report_type='monthly_insights',
                    title=f"Monthly Insights - {client.name}",
                    content=f"Monthly performance insights for {client.name}",
                    kpi_data=insight_data,
                    generated_at=datetime.now()
                )
                
                insights_generated += 1
        
        logger.info(f"Generated monthly insights for {insights_generated} clients")
        return f"{insights_generated} monthly insights generated"
        
    except Exception as e:
        logger.error(f"Error generating monthly insights: {str(e)}")
        raise

def fetch_all_google_ads_data():
    for cred in GoogleAdsCredential.objects.all():
        # Fetch data using the stored credentials
        data = fetch_google_ads_data(
            refresh_token=cred.refresh_token,
            client_id=cred.google_client_id,
            client_secret=cred.client_secret,
            developer_token=cred.developer_token
        )
        # TODO: Save data to the database, linked to cred.client
        # Example: GoogleAdsData.objects.create(client=cred.client, data=data, fetched_at=timezone.now())

# Schedule this task to run every hour
schedule('dashboard.tasks.fetch_all_google_ads_data', schedule_type='H')

# Mailchimp

def fetch_all_mailchimp_data():
    for cred in MailchimpCredential.objects.all():
        data = fetch_mailchimp_data(
            api_key=cred.api_key,
            server_prefix=cred.server_prefix
        )
        # TODO: Save data to the database, linked to cred.client
        # Example: MailchimpData.objects.create(client=cred.client, data=data, fetched_at=timezone.now())

schedule('dashboard.tasks.fetch_all_mailchimp_data', schedule_type='H')

# LinkedIn Ads

def fetch_all_linkedin_ads_data():
    for cred in LinkedInAdsCredential.objects.all():
        data = fetch_linkedin_ads_data(
            access_token=cred.access_token
        )
        # TODO: Save data to the database, linked to cred.client
        # Example: LinkedInAdsData.objects.create(client=cred.client, data=data, fetched_at=timezone.now())

schedule('dashboard.tasks.fetch_all_linkedin_ads_data', schedule_type='H')

# Zoho

def fetch_all_zoho_data():
    for cred in ZohoCredential.objects.all():
        data = fetch_zoho_data(
            access_token=cred.access_token,
            refresh_token=cred.refresh_token,
            client_id=cred.zoho_client_id,
            client_secret=cred.client_secret
        )
        # TODO: Save data to the database, linked to cred.client
        # Example: ZohoData.objects.create(client=cred.client, data=data, fetched_at=timezone.now())

schedule('dashboard.tasks.fetch_all_zoho_data', schedule_type='H') 