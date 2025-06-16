import pandas as pd
import logging
from typing import Dict, List

def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute key performance indicators for the marketing data.
    
    Args:
        df: Cleaned dataframe with marketing metrics
        
    Returns:
        pd.DataFrame: Dataframe with additional KPI columns
    """
    try:
        # Create a copy to avoid modifying the original dataframe
        df = df.copy()
        
        # Calculate KPIs
        df['CTR'] = (df['Clicks'] / df['Impressions'].replace(0, 1)) * 100
        df['CPC'] = df['Cost'] / df['Clicks'].replace(0, 1)
        df['Conversion Rate'] = (df['Conversions'] / df['Clicks'].replace(0, 1)) * 100
        df['ROAS'] = df['Revenue'] / df['Cost'].replace(0, 1)
        df['CPA'] = df['Cost'] / df['Conversions'].replace(0, 1)
        
        # Round numeric columns to 2 decimal places
        numeric_cols = ['CTR', 'CPC', 'Conversion Rate', 'ROAS', 'CPA']
        df[numeric_cols] = df[numeric_cols].round(2)
        
        return df
        
    except Exception as e:
        logging.error(f"Error computing KPIs: {str(e)}")
        raise

def get_summary_stats(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate summary statistics for the dataset.
    
    Args:
        df: Dataframe with marketing metrics and KPIs
        
    Returns:
        Dict[str, float]: Dictionary containing summary statistics
    """
    try:
        summary = {
            'Total Impressions': df['Impressions'].sum(),
            'Total Clicks': df['Clicks'].sum(),
            'Total Cost': df['Cost'].sum(),
            'Total Conversions': df['Conversions'].sum(),
            'Total Revenue': df['Revenue'].sum(),
            'Average CTR': df['CTR'].mean(),
            'Average CPC': df['CPC'].mean(),
            'Average ROAS': df['ROAS'].mean(),
            'Average CPA': df['CPA'].mean()
        }
        
        # Round numeric values to 2 decimal places
        summary = {k: round(v, 2) if isinstance(v, float) else v 
                  for k, v in summary.items()}
        
        return summary
        
    except Exception as e:
        logging.error(f"Error calculating summary stats: {str(e)}")
        raise 