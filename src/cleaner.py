import pandas as pd
import logging
from typing import Union, Optional

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the input data.
    
    Args:
        df: Input DataFrame with marketing metrics
        
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    try:
        # Create a copy to avoid modifying the original dataframe
        df = df.copy()
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.title()
        
        # Define expected columns
        expected_cols = [
            'Date', 'Campaign Name', 'Impressions', 
            'Clicks', 'Cost', 'Conversions', 'Revenue'
        ]
        
        # Add missing columns with default value 0
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
                logging.warning(f"Missing column '{col}' added with default value 0")
        
        # Convert date column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Handle missing values
        df.fillna(0, inplace=True)
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Ensure numeric columns are float
        numeric_cols = ['Impressions', 'Clicks', 'Cost', 'Conversions', 'Revenue']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        logging.error(f"Error cleaning data: {str(e)}")
        raise 