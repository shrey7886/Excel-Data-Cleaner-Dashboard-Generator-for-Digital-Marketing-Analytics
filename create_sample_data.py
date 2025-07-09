import os
import csv
import json
from random import randint, uniform, choice
from datetime import datetime, timedelta

# Ensure sample_data directory exists
os.makedirs('sample_data', exist_ok=True)

# Helper to generate random dates
base_date = datetime(2024, 5, 1)
def random_date(offset):
    return (base_date + timedelta(days=30*offset)).strftime('%Y-%m-%d')

campaigns = ['Spring Sale', 'Summer Blast', 'Autumn Promo', 'Winter Deals']
demographics = ['Marketing', 'Sales', 'IT', 'HR']

# Mailchimp CSV
data_mailchimp = [
    ['campaign_name', 'date', 'open_rate', 'click_rate'],
]
for i, c in enumerate(campaigns):
    data_mailchimp.append([
        c,
        random_date(i),
        round(uniform(0.20, 0.40), 2),
        round(uniform(0.08, 0.15), 2)
    ])
with open('sample_data/mailchimp_sample.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data_mailchimp)

# Zoho CRM JSON
data_zoho = []
for i, c in enumerate(campaigns):
    data_zoho.append({
        'lead_id': i+1,
        'campaign_name': c,
        'date': random_date(i),
        'leads': randint(80, 150),
        'deals': randint(8, 20)
    })
with open('sample_data/zoho_sample.json', 'w') as f:
    json.dump(data_zoho, f, indent=2)

# Demandbase JSON
data_demandbase = []
for i, c in enumerate(campaigns):
    data_demandbase.append({
        'campaign_name': c,
        'date': random_date(i),
        'intent_score': randint(50, 90)
    })
with open('sample_data/demandbase_sample.json', 'w') as f:
    json.dump(data_demandbase, f, indent=2)

# Google Ads CSV
data_google = [
    ['campaign_name', 'date', 'impressions', 'clicks', 'spend', 'ctr'],
]
for i, c in enumerate(campaigns):
    impressions = randint(7000, 15000)
    clicks = randint(200, 500)
    spend = randint(300, 800)
    ctr = round(clicks / impressions, 4)
    data_google.append([
        c,
        random_date(i),
        impressions,
        clicks,
        spend,
        ctr
    ])
with open('sample_data/google_ads_sample.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data_google)

# LinkedIn Ads CSV
data_linkedin = [
    ['campaign_name', 'date', 'cpl', 'demographic', 'spend', 'conversions'],
]
for i, c in enumerate(campaigns):
    cpl = round(uniform(20, 35), 2)
    demographic = choice(demographics)
    spend = randint(200, 400)
    conversions = randint(5, 15)
    data_linkedin.append([
        c,
        random_date(i),
        cpl,
        demographic,
        spend,
        conversions
    ])
with open('sample_data/linkedin_ads_sample.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(data_linkedin)

print('Sample data files created in sample_data/') 