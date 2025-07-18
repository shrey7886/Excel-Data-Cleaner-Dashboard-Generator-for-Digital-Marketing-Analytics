import os
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def fetch_google_ads_data(client=None):
    """
    Fetch real Google Ads data using the Google Ads API.
    Args:
        client: (optional) Django client object with credentials.
    Returns:
        pd.DataFrame: DataFrame with Google Ads data.
    """
    try:
        # Load credentials from file or environment
        config_path = os.getenv('GOOGLE_ADS_YAML_PATH', 'google-ads.yaml')
        googleads_client = GoogleAdsClient.load_from_storage(config_path)

        # Example: Fetch campaign data
        ga_service = googleads_client.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
        """
        response = ga_service.search_stream(customer_id="INSERT_CUSTOMER_ID", query=query)
        data = []
        for batch in response:
            for row in batch.results:
                data.append({
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "spend": row.metrics.cost_micros / 1e6,
                })
        return pd.DataFrame(data)
    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")
        return pd.DataFrame([])
    except Exception as e:
        print(f"Google Ads integration error: {e}")
        return pd.DataFrame([])
