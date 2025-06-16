import os
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from cleaner import clean_data
from kpi_calculator import compute_kpis, get_summary_stats
from dashboard_generator import create_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def run_pipeline(input_file: str, output_dir: Optional[str] = None) -> str:
    """
    Run the complete data processing and dashboard generation pipeline.
    
    Args:
        input_file: Path to the input Excel file
        output_dir: Optional directory to save the output. Defaults to 'output'
        
    Returns:
        str: Path to the generated dashboard file
    """
    try:
        # Set up output directory
        if output_dir is None:
            output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'dashboard_{timestamp}.xlsx')
        
        # Process the data
        logging.info(f"Reading and cleaning data from {input_file}")
        df = clean_data(input_file)
        
        logging.info("Computing KPIs")
        df = compute_kpis(df)
        
        logging.info("Generating summary statistics")
        summary_stats = get_summary_stats(df)
        
        logging.info(f"Creating dashboard at {output_file}")
        create_dashboard(df, output_file)
        
        logging.info("Pipeline completed successfully")
        return output_file
        
    except Exception as e:
        logging.error(f"Error in pipeline: {str(e)}")
        raise

def main():
    """Main entry point for the application."""
    try:
        # Get input file from command line or use default
        import sys
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
        else:
            input_file = 'input/sample_data.xlsx'
        
        # Ensure input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Run the pipeline
        output_file = run_pipeline(input_file)
        print(f"\nDashboard generated successfully!")
        print(f"Output file: {output_file}")
        
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 