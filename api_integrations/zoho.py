import os
import pandas as pd
import requests

def fetch_zoho_data(client=None):
    """
    Fetch real Zoho CRM data using the Zoho API.
    Args:
        client: (optional) Django client object with credentials.
    Returns:
        pd.DataFrame: DataFrame with Zoho CRM data.
    """
    try:
        access_token = os.getenv('ZOHO_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')
        org_id = os.getenv('ZOHO_ORG_ID', 'YOUR_ORG_ID')
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "orgId": org_id
        }
        url = "https://www.zohoapis.com/crm/v2/Leads"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", [])
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Zoho API error: {e}")
        return pd.DataFrame([])
