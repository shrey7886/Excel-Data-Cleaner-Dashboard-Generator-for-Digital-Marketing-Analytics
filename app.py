import streamlit as st
import pandas as pd
from src.cleaner import clean_data
from src.kpi_calculator import compute_kpis
from src.dashboard_generator import create_dashboard
import logging
import os
from datetime import datetime
import io

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_file(uploaded_file):
    """Process the uploaded file and return a DataFrame."""
    try:
        # Read the file content
        bytes_data = uploaded_file.getvalue()
        
        # Create a BytesIO object
        excel_file = io.BytesIO(bytes_data)
        
        # Read the Excel file
        df = pd.read_excel(excel_file, engine='openpyxl')
        logging.info(f"Successfully read Excel file. Shape: {df.shape}")
        
        return df
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise

def validate_dataframe(df):
    """Validate the DataFrame structure and data types."""
    try:
        required_columns = {
            'Date': 'datetime64[ns]',
            'Campaign Name': 'str',
            'Impressions': 'float64',
            'Clicks': 'float64',
            'Cost': 'float64',
            'Conversions': 'float64',
            'Revenue': 'float64'
        }
        
        # Check for missing columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logging.warning(f"Missing columns: {missing_cols}")
            for col in missing_cols:
                dtype = required_columns[col]
                if dtype == 'datetime64[ns]':
                    df[col] = pd.Timestamp.now()
                elif dtype == 'str':
                    df[col] = 'Unknown'
                else:
                    df[col] = 0.0
        
        # Convert column types
        for col, dtype in required_columns.items():
            try:
                if col in df.columns:
                    if dtype == 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    elif dtype == 'str':
                        df[col] = df[col].astype(str)
                    else:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            except Exception as e:
                logging.warning(f"Could not convert column '{col}' to {dtype}: {str(e)}")
                if dtype == 'datetime64[ns]':
                    df[col] = pd.Timestamp.now()
                elif dtype == 'str':
                    df[col] = df[col].astype(str)
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        return df
    except Exception as e:
        logging.error(f"Error validating DataFrame: {str(e)}")
        raise

def main():
    st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")
    
    st.title("Targetorate Marketing Analytics Dashboard")
    st.write("Upload your marketing data Excel file to generate a comprehensive dashboard.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Process the file
            df = process_file(uploaded_file)
            
            # Validate and clean the data
            df = validate_dataframe(df)
            df = clean_data(df)
            
            # Compute KPIs
            df = compute_kpis(df)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/dashboard_{timestamp}.xlsx"
            
            # Create output directory if it doesn't exist
            os.makedirs('output', exist_ok=True)
            
            # Create dashboard
            create_dashboard(df, output_file)
            
            # Show success message
            st.success("Dashboard generated successfully!")
            
            # Display preview of the data
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Display key metrics
            st.subheader("Key Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Revenue", f"${df['Revenue'].sum():,.2f}")
                st.metric("Average ROAS", f"{df['ROAS'].mean():.2f}")
            
            with col2:
                st.metric("Total Cost", f"${df['Cost'].sum():,.2f}")
                st.metric("Average CTR", f"{df['CTR'].mean():.2%}")
            
            with col3:
                st.metric("Total Conversions", f"{df['Conversions'].sum():,.0f}")
                st.metric("Average CPC", f"${df['CPC'].mean():.2f}")
            
            # Add download button for the generated dashboard
            with open(output_file, 'rb') as f:
                st.download_button(
                    label="Download Dashboard",
                    data=f,
                    file_name=f"dashboard_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logging.error(f"Error in Streamlit app: {str(e)}")

if __name__ == "__main__":
    main() 