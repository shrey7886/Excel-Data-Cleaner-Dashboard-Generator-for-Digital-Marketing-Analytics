import os
import pandas as pd
import requests

def fetch_demandbase_data(client=None):
    """
    Fetch real Demandbase data using the Demandbase API.
    Args:
        client: (optional) Django client object with credentials.
    Returns:
        pd.DataFrame: DataFrame with Demandbase data.
    """
    try:
        api_key = os.getenv('DEMANDBASE_API_KEY', 'YOUR_API_KEY')
        headers = {"Authorization": f"Bearer {api_key}"}
        url = "https://api.demandbase.com/v2/accounts"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("accounts", [])
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Demandbase API error: {e}")
        return pd.DataFrame([])
