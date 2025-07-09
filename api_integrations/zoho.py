import pandas as pd

def fetch_zoho_data():
    """Simulate fetching Zoho CRM campaign data."""
    data = [
        {"lead_id": 1, "campaign_name": "Spring Sale", "date": "2024-05-01", "leads": 136, "deals": 19},
        {"lead_id": 2, "campaign_name": "Summer Blast", "date": "2024-05-31", "leads": 125, "deals": 18},
        {"lead_id": 3, "campaign_name": "Autumn Promo", "date": "2024-06-30", "leads": 146, "deals": 15},
        {"lead_id": 4, "campaign_name": "Winter Deals", "date": "2024-07-30", "leads": 95, "deals": 13},
        {"lead_id": 5, "campaign_name": "Holiday Blast", "date": "2024-08-15", "leads": 110, "deals": 16},
        {"lead_id": 6, "campaign_name": "Back to School", "date": "2024-09-01", "leads": 120, "deals": 14},
        {"lead_id": 7, "campaign_name": "Black Friday", "date": "2024-11-29", "leads": 200, "deals": 30},
        {"lead_id": 8, "campaign_name": "Cyber Monday", "date": "2024-12-02", "leads": 180, "deals": 28},
    ]
    return pd.DataFrame(data) 