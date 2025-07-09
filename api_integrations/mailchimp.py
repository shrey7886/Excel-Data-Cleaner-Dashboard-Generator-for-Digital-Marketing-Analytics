import pandas as pd

def fetch_mailchimp_data():
    """Simulate fetching Mailchimp campaign data."""
    data = [
        {"campaign_name": "Spring Sale", "date": "2024-05-01", "open_rate": 0.29, "click_rate": 0.09},
        {"campaign_name": "Summer Blast", "date": "2024-05-31", "open_rate": 0.32, "click_rate": 0.12},
        {"campaign_name": "Autumn Promo", "date": "2024-06-30", "open_rate": 0.37, "click_rate": 0.12},
        {"campaign_name": "Winter Deals", "date": "2024-07-30", "open_rate": 0.35, "click_rate": 0.10},
        {"campaign_name": "Holiday Blast", "date": "2024-08-15", "open_rate": 0.41, "click_rate": 0.15},
        {"campaign_name": "Back to School", "date": "2024-09-01", "open_rate": 0.28, "click_rate": 0.08},
        {"campaign_name": "Black Friday", "date": "2024-11-29", "open_rate": 0.45, "click_rate": 0.18},
        {"campaign_name": "Cyber Monday", "date": "2024-12-02", "open_rate": 0.43, "click_rate": 0.17},
    ]
    return pd.DataFrame(data) 