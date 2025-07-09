import pandas as pd

def fetch_google_ads_data():
    """Simulate fetching Google Ads campaign data."""
    data = [
        {"campaign_name": "Spring Sale", "date": "2024-05-01", "impressions": 12262, "clicks": 336, "spend": 550, "ctr": 0.0274},
        {"campaign_name": "Summer Blast", "date": "2024-05-31", "impressions": 8270, "clicks": 217, "spend": 494, "ctr": 0.0262},
        {"campaign_name": "Autumn Promo", "date": "2024-06-30", "impressions": 12522, "clicks": 439, "spend": 755, "ctr": 0.0351},
        {"campaign_name": "Winter Deals", "date": "2024-07-30", "impressions": 9430, "clicks": 314, "spend": 491, "ctr": 0.0333},
        {"campaign_name": "Holiday Blast", "date": "2024-08-15", "impressions": 11000, "clicks": 400, "spend": 600, "ctr": 0.0364},
        {"campaign_name": "Back to School", "date": "2024-09-01", "impressions": 9000, "clicks": 250, "spend": 480, "ctr": 0.0278},
        {"campaign_name": "Black Friday", "date": "2024-11-29", "impressions": 20000, "clicks": 900, "spend": 1500, "ctr": 0.0450},
        {"campaign_name": "Cyber Monday", "date": "2024-12-02", "impressions": 18000, "clicks": 850, "spend": 1400, "ctr": 0.0472},
    ]
    return pd.DataFrame(data) 