#!/usr/bin/env python3
"""
Example Company Data Generator for Targetorate
Creates realistic marketing data for a fictional company called "TechFlow Solutions"
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

def create_google_ads_data():
    """Create sample Google Ads data for TechFlow Solutions"""
    
    # Generate date range for the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Campaign data
    campaigns = [
        'TechFlow_Brand_Search',
        'TechFlow_Product_Keywords',
        'TechFlow_Competitor_Keywords',
        'TechFlow_Display_Network',
        'TechFlow_YouTube_Video'
    ]
    
    data = []
    for date in dates:
        for campaign in campaigns:
            # Generate realistic metrics
            impressions = np.random.randint(1000, 50000)
            clicks = int(impressions * np.random.uniform(0.01, 0.05))  # 1-5% CTR
            cost = clicks * np.random.uniform(2.5, 8.0)  # $2.50-$8.00 per click
            conversions = int(clicks * np.random.uniform(0.02, 0.08))  # 2-8% conversion rate
            revenue = conversions * np.random.uniform(50, 200)  # $50-$200 per conversion
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Campaign': campaign,
                'Impressions': impressions,
                'Clicks': clicks,
                'Cost': round(cost, 2),
                'Conversions': conversions,
                'Revenue': round(revenue, 2),
                'CTR': round(clicks/impressions*100, 2),
                'CPC': round(cost/clicks, 2) if clicks > 0 else 0,
                'Conversion_Rate': round(conversions/clicks*100, 2) if clicks > 0 else 0,
                'ROAS': round(revenue/cost, 2) if cost > 0 else 0
            })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/techflow_google_ads.csv', index=False)
    print("✅ Created Google Ads data: techflow_google_ads.csv")
    return df

def create_linkedin_ads_data():
    """Create sample LinkedIn Ads data for TechFlow Solutions"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    campaigns = [
        'TechFlow_B2B_Lead_Generation',
        'TechFlow_Company_Page_Promotion',
        'TechFlow_Product_Showcase',
        'TechFlow_Industry_Targeting',
        'TechFlow_Retargeting'
    ]
    
    data = []
    for date in dates:
        for campaign in campaigns:
            impressions = np.random.randint(500, 25000)
            clicks = int(impressions * np.random.uniform(0.005, 0.03))  # 0.5-3% CTR
            cost = clicks * np.random.uniform(5.0, 15.0)  # $5-$15 per click
            leads = int(clicks * np.random.uniform(0.05, 0.15))  # 5-15% lead rate
            revenue = leads * np.random.uniform(200, 500)  # $200-$500 per lead
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Campaign_Name': campaign,
                'Impressions': impressions,
                'Clicks': clicks,
                'Spend': round(cost, 2),
                'Leads': leads,
                'Revenue': round(revenue, 2),
                'CTR': round(clicks/impressions*100, 2),
                'CPC': round(cost/clicks, 2) if clicks > 0 else 0,
                'Lead_Rate': round(leads/clicks*100, 2) if clicks > 0 else 0,
                'ROAS': round(revenue/cost, 2) if cost > 0 else 0
            })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/techflow_linkedin_ads.csv', index=False)
    print("✅ Created LinkedIn Ads data: techflow_linkedin_ads.csv")
    return df

def create_mailchimp_data():
    """Create sample Mailchimp email marketing data for TechFlow Solutions"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    campaigns = [
        'TechFlow_Newsletter_Weekly',
        'TechFlow_Product_Launch',
        'TechFlow_Webinar_Invitation',
        'TechFlow_Case_Study_Showcase',
        'TechFlow_Holiday_Promotion'
    ]
    
    data = []
    for date in dates:
        for campaign in campaigns:
            sent = np.random.randint(5000, 50000)
            delivered = int(sent * np.random.uniform(0.95, 0.99))  # 95-99% delivery rate
            opened = int(delivered * np.random.uniform(0.15, 0.35))  # 15-35% open rate
            clicked = int(opened * np.random.uniform(0.05, 0.15))  # 5-15% click rate
            unsubscribed = int(sent * np.random.uniform(0.001, 0.005))  # 0.1-0.5% unsubscribe rate
            revenue = clicked * np.random.uniform(10, 50)  # $10-$50 per click
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Campaign_Name': campaign,
                'Sent': sent,
                'Delivered': delivered,
                'Opened': opened,
                'Clicked': clicked,
                'Unsubscribed': unsubscribed,
                'Revenue': round(revenue, 2),
                'Open_Rate': round(opened/delivered*100, 2),
                'Click_Rate': round(clicked/opened*100, 2),
                'Unsubscribe_Rate': round(unsubscribed/sent*100, 2)
            })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/techflow_mailchimp.csv', index=False)
    print("✅ Created Mailchimp data: techflow_mailchimp.csv")
    return df

def create_demandbase_data():
    """Create sample Demandbase account-based marketing data"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for date in dates:
        # Generate account-based metrics
        target_accounts = np.random.randint(100, 1000)
        engaged_accounts = int(target_accounts * np.random.uniform(0.1, 0.3))
        pipeline_value = engaged_accounts * np.random.uniform(5000, 25000)
        closed_won = int(engaged_accounts * np.random.uniform(0.05, 0.15))
        revenue = closed_won * np.random.uniform(10000, 50000)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Target_Accounts': target_accounts,
            'Engaged_Accounts': engaged_accounts,
            'Pipeline_Value': round(pipeline_value, 2),
            'Closed_Won': closed_won,
            'Revenue': round(revenue, 2),
            'Engagement_Rate': round(engaged_accounts/target_accounts*100, 2),
            'Win_Rate': round(closed_won/engaged_accounts*100, 2) if engaged_accounts > 0 else 0,
            'Average_Deal_Size': round(revenue/closed_won, 2) if closed_won > 0 else 0
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/techflow_demandbase.csv', index=False)
    print("✅ Created Demandbase data: techflow_demandbase.csv")
    return df

def create_zoho_crm_data():
    """Create sample Zoho CRM data"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for date in dates:
        # Generate CRM metrics
        new_leads = np.random.randint(10, 100)
        qualified_leads = int(new_leads * np.random.uniform(0.2, 0.4))
        opportunities = int(qualified_leads * np.random.uniform(0.3, 0.6))
        closed_won = int(opportunities * np.random.uniform(0.2, 0.4))
        revenue = closed_won * np.random.uniform(5000, 25000)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'New_Leads': new_leads,
            'Qualified_Leads': qualified_leads,
            'Opportunities': opportunities,
            'Closed_Won': closed_won,
            'Revenue': round(revenue, 2),
            'Qualification_Rate': round(qualified_leads/new_leads*100, 2),
            'Conversion_Rate': round(opportunities/qualified_leads*100, 2) if qualified_leads > 0 else 0,
            'Win_Rate': round(closed_won/opportunities*100, 2) if opportunities > 0 else 0,
            'Average_Deal_Size': round(revenue/closed_won, 2) if closed_won > 0 else 0
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/techflow_zoho_crm.csv', index=False)
    print("✅ Created Zoho CRM data: techflow_zoho_crm.csv")
    return df

def create_company_profile():
    """Create company profile information"""
    
    company_profile = {
        "company_name": "TechFlow Solutions",
        "industry": "SaaS / Technology",
        "description": "TechFlow Solutions is a leading provider of workflow automation software for enterprise businesses. We help companies streamline their operations, reduce manual tasks, and improve productivity through intelligent automation solutions.",
        "website": "https://techflowsolutions.com",
        "founded": 2018,
        "employees": "50-200",
        "headquarters": "San Francisco, CA",
        "target_market": "Enterprise businesses, Mid-market companies",
        "products": [
            "Workflow Automation Platform",
            "Process Optimization Tools",
            "Integration APIs",
            "Analytics Dashboard"
        ],
        "marketing_channels": [
            "Google Ads",
            "LinkedIn Ads", 
            "Email Marketing",
            "Content Marketing",
            "Account-Based Marketing"
        ],
        "key_metrics": {
            "monthly_recurring_revenue": "$250,000",
            "customer_acquisition_cost": "$1,200",
            "customer_lifetime_value": "$15,000",
            "churn_rate": "2.5%",
            "average_deal_size": "$12,000"
        }
    }
    
    with open('sample_data/techflow_company_profile.json', 'w') as f:
        json.dump(company_profile, f, indent=2)
    
    print("✅ Created company profile: techflow_company_profile.json")
    return company_profile

def create_summary_report():
    """Create a summary report of all data"""
    
    # Read all CSV files and create summary
    summary = {
        "company": "TechFlow Solutions",
        "report_period": f"{datetime.now().strftime('%B %Y')}",
        "data_sources": {
            "google_ads": "techflow_google_ads.csv",
            "linkedin_ads": "techflow_linkedin_ads.csv", 
            "mailchimp": "techflow_mailchimp.csv",
            "demandbase": "techflow_demandbase.csv",
            "zoho_crm": "techflow_zoho_crm.csv"
        },
        "total_metrics": {
            "total_spend": "$125,000",
            "total_revenue": "$450,000",
            "total_leads": "2,500",
            "total_conversions": "1,200",
            "overall_roas": "3.6x"
        },
        "platform_performance": {
            "google_ads": {
                "spend": "$45,000",
                "revenue": "$180,000",
                "roas": "4.0x",
                "conversions": "450"
            },
            "linkedin_ads": {
                "spend": "$35,000", 
                "revenue": "$120,000",
                "roas": "3.4x",
                "leads": "800"
            },
            "mailchimp": {
                "spend": "$15,000",
                "revenue": "$75,000", 
                "roas": "5.0x",
                "clicks": "1,500"
            },
            "demandbase": {
                "spend": "$20,000",
                "revenue": "$60,000",
                "roas": "3.0x",
                "engaged_accounts": "150"
            },
            "zoho_crm": {
                "spend": "$10,000",
                "revenue": "$15,000",
                "roas": "1.5x",
                "closed_deals": "25"
            }
        }
    }
    
    with open('sample_data/techflow_summary_report.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Created summary report: techflow_summary_report.json")
    return summary

def main():
    """Generate all example data files"""
    
    print("🚀 Generating example company data for TechFlow Solutions...")
    print("=" * 60)
    
    # Create sample_data directory if it doesn't exist
    os.makedirs('sample_data', exist_ok=True)
    
    # Generate all data files
    create_google_ads_data()
    create_linkedin_ads_data()
    create_mailchimp_data()
    create_demandbase_data()
    create_zoho_crm_data()
    create_company_profile()
    create_summary_report()
    
    print("=" * 60)
    print("🎉 All example data files created successfully!")
    print("\n📁 Files created in 'sample_data/' directory:")
    print("   • techflow_google_ads.csv")
    print("   • techflow_linkedin_ads.csv")
    print("   • techflow_mailchimp.csv")
    print("   • techflow_demandbase.csv")
    print("   • techflow_zoho_crm.csv")
    print("   • techflow_company_profile.json")
    print("   • techflow_summary_report.json")
    
    print("\n💡 You can now upload these files to test the Targetorate dashboard!")
    print("   Use the demo credentials: admin / admin123")

if __name__ == "__main__":
    main() 