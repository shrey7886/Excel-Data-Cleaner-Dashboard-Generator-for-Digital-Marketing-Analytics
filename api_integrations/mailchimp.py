import os
import pandas as pd
from mailchimp3 import MailChimp

def fetch_mailchimp_data(client=None):
    """
    Fetch real Mailchimp data using the Mailchimp API.
    Args:
        client: (optional) Django client object with credentials.
    Returns:
        pd.DataFrame: DataFrame with Mailchimp data.
    """
    try:
        api_key = os.getenv('MAILCHIMP_API_KEY', 'YOUR_API_KEY')
        username = os.getenv('MAILCHIMP_USERNAME', 'YOUR_USERNAME')
        client = MailChimp(mc_api=api_key, mc_user=username)
        # Example: Fetch campaign reports
        reports = client.reports.all(get_all=True, fields="reports.id,reports.campaign_title,reports.emails_sent,reports.opens.total_opens,reports.clicks.total_clicks")
        data = reports.get('reports', [])
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Mailchimp API error: {e}")
        return pd.DataFrame([])
