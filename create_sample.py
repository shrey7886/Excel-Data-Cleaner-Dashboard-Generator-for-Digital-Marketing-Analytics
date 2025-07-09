import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data():
    # Create date range for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create sample campaign names
    campaign_types = ['Google', 'Meta', 'LinkedIn']
    regions = ['India', 'US']
    campaign_types_full = []
    for ctype in campaign_types:
        for region in regions:
            campaign_types_full.append(f"{ctype} Ads - {region}")
            campaign_types_full.append(f"{ctype} Organic - {region}")

    # Generate random data
    np.random.seed(42)  # For reproducibility
    n_days = len(dates)
    n_campaigns = len(campaign_types_full)

    data = []
    for date in dates:
        for campaign in campaign_types_full:
            # Base metrics
            impressions = np.random.randint(1000, 10000)
            clicks = np.random.randint(50, impressions)
            cost = np.random.uniform(100, 1000)
            conversions = np.random.randint(0, clicks)
            revenue = np.random.uniform(200, 2000)

            # Adjust metrics based on campaign type
            if 'Organic' in campaign:
                cost = 0  # Organic campaigns have no cost
                revenue *= 0.7  # Organic typically has lower revenue
            if 'India' in campaign:
                revenue *= 0.8  # India market typically has lower revenue
                cost *= 0.7  # India market typically has lower costs

            data.append({
                'Date': date,
                'Campaign Name': campaign,
                'Impressions': impressions,
                'Clicks': clicks,
                'Cost': round(cost, 2),
                'Conversions': conversions,
                'Revenue': round(revenue, 2)
            })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create input directory if it doesn't exist
    os.makedirs('input', exist_ok=True)

    # Save to Excel
    output_file = 'input/marketing_data_example.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Sample data created and saved to {output_file}")
    print("\nSample data preview:")
    print(df.head())
    print("\nData shape:", df.shape)
    print("\nColumns:", df.columns.tolist())

if __name__ == "__main__":
    create_sample_data() 