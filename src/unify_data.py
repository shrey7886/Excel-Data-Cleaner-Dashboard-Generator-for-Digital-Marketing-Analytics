import pandas as pd
from normalize_mailchimp import normalize_mailchimp
from normalize_zoho import normalize_zoho
from normalize_demandbase import normalize_demandbase
from normalize_google_ads import normalize_google_ads
from normalize_linkedin_ads import normalize_linkedin_ads

def unify_all_data():
    dfs = [
        normalize_mailchimp(),
        normalize_zoho(),
        normalize_demandbase(),
        normalize_google_ads(),
        normalize_linkedin_ads(),
    ]
    unified_df = pd.concat(dfs, ignore_index=True)
    return unified_df

if __name__ == "__main__":
    df = unify_all_data()
    print(df.head())
    # Optionally, save to CSV for inspection
    df.to_csv("output/unified_campaign_data.csv", index=False) 