import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate date range for the last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Generate sample data
n_days = len(dates)
campaigns = ['Summer Sale', 'Brand Awareness', 'Product Launch', 'Holiday Special', 'Clearance Sale']

data = {
    'Date': np.random.choice(dates, n_days),
    'Campaign Name': np.random.choice(campaigns, n_days),
    'Impressions': np.random.randint(1000, 10000, n_days),
    'Clicks': np.random.randint(100, 1000, n_days),
    'Cost': np.random.uniform(100, 1000, n_days).round(2),
    'Conversions': np.random.randint(10, 100, n_days),
    'Revenue': np.random.uniform(500, 5000, n_days).round(2)
}

# Create DataFrame
df = pd.DataFrame(data)

# Sort by date
df = df.sort_values('Date')

# Create output directory if it doesn't exist
import os
os.makedirs('input', exist_ok=True)

# Save to Excel
output_file = 'input/marketing_data_sample.xlsx'
df.to_excel(output_file, index=False)

print(f"Sample data has been created and saved to {output_file}")
print("\nData Preview:")
print(df.head()) 