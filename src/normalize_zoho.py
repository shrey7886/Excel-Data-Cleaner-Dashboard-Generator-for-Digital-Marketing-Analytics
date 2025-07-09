import pandas as pd
from api_integrations.zoho import fetch_zoho_data

def normalize_zoho():
    df = fetch_zoho_data()
    df['platform'] = 'Zoho'
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