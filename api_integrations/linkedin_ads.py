import pandas as pd

def fetch_linkedin_ads_data():
    """Simulate fetching LinkedIn Ads campaign data."""
    data = [
        {"campaign_name": "Spring Sale", "date": "2024-05-01", "cpl": 31.64, "demographic": "IT", "spend": 252, "conversions": 15},
        {"campaign_name": "Summer Blast", "date": "2024-05-31", "cpl": 25.81, "demographic": "HR", "spend": 378, "conversions": 7},
        {"campaign_name": "Autumn Promo", "date": "2024-06-30", "cpl": 34.27, "demographic": "IT", "spend": 357, "conversions": 8},
        {"campaign_name": "Winter Deals", "date": "2024-07-30", "cpl": 34.0, "demographic": "IT", "spend": 380, "conversions": 11},
        {"campaign_name": "Holiday Blast", "date": "2024-08-15", "cpl": 29.50, "demographic": "Finance", "spend": 400, "conversions": 13},
        {"campaign_name": "Back to School", "date": "2024-09-01", "cpl": 27.80, "demographic": "Education", "spend": 320, "conversions": 10},
        {"campaign_name": "Black Friday", "date": "2024-11-29", "cpl": 22.10, "demographic": "Retail", "spend": 600, "conversions": 25},
        {"campaign_name": "Cyber Monday", "date": "2024-12-02", "cpl": 23.50, "demographic": "Retail", "spend": 580, "conversions": 22},
    ]
    return pd.DataFrame(data) 