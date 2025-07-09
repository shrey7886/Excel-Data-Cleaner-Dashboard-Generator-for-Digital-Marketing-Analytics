import pandas as pd
from api_integrations.mailchimp import fetch_mailchimp_data

def normalize_mailchimp():
    df = fetch_mailchimp_data()
    df['platform'] = 'Mailchimp'
    # Unified schema columns
    unified_cols = [
        'campaign_name', 'platform', 'date', 'impressions', 'clicks', 'spend',
        'open_rate', 'click_rate', 'conversions', 'leads', 'deals', 'intent_score', 'cpl', 'demographic'
    ]
    # Add missing columns
    for col in unified_cols:
        if col not in df.columns:
            df[col] = None
    # Reorder columns
    df = df[unified_cols]
    return df 