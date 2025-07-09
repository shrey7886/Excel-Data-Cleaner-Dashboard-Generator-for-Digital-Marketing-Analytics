import pandas as pd
from api_integrations.google_ads import fetch_google_ads_data

def normalize_google_ads():
    df = fetch_google_ads_data()
    df['platform'] = 'Google Ads'
    # Rename spend to match unified schema
    if 'cost' in df.columns:
        df.rename(columns={'cost': 'spend'}, inplace=True)
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