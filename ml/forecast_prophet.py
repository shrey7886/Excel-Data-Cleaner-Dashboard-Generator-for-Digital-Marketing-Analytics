import pandas as pd
import numpy as np
from prophet import Prophet
import pickle
import os
from datetime import datetime, timedelta

def train_prophet_models():
    """Train Prophet models for time series forecasting."""
    
    # Load unified data
    df = pd.read_csv('output/unified_campaign_data.csv')
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Aggregate data by date for time series analysis
    daily_metrics = df.groupby('date').agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'spend': 'sum',
        'conversions': 'sum',
        'leads': 'sum',
        'deals': 'sum'
    }).reset_index()
    
    # Calculate daily KPIs
    daily_metrics['ctr'] = daily_metrics['clicks'] / daily_metrics['impressions']
    daily_metrics['cpa'] = daily_metrics['spend'] / daily_metrics['conversions'].fillna(1)
    daily_metrics['conversion_rate'] = daily_metrics['conversions'] / daily_metrics['clicks'].fillna(1)
    
    # Fill missing dates with 0 values
    date_range = pd.date_range(start=daily_metrics['date'].min(), 
                              end=daily_metrics['date'].max(), 
                              freq='D')
    daily_metrics = daily_metrics.set_index('date').reindex(date_range, fill_value=0).reset_index()
    daily_metrics.rename(columns={'index': 'date'}, inplace=True)
    
    # Train Prophet models for different metrics
    models = {}
    forecasts = {}
    
    metrics_to_forecast = ['impressions', 'clicks', 'spend', 'ctr', 'cpa']
    
    for metric in metrics_to_forecast:
        if metric in daily_metrics.columns:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            prophet_data = daily_metrics[['date', metric]].copy()
            prophet_data.columns = ['ds', 'y']
            
            # Remove infinite values
            prophet_data = prophet_data[np.isfinite(prophet_data['y'])]
            
            if len(prophet_data) > 7:  # Need at least a week of data
                # Create and fit Prophet model
                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=False,
                    seasonality_mode='multiplicative'
                )
                
                # Add custom seasonality for business days
                model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
                
                model.fit(prophet_data)
                
                # Make future predictions (next 30 days)
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)
                
                models[metric] = model
                forecasts[metric] = forecast
                
                print(f"Prophet model trained for {metric}")
                print(f"Forecast range: {forecast['ds'].min()} to {forecast['ds'].max()}")
    
    # Save models and forecasts
    prophet_data = {
        'models': models,
        'forecasts': forecasts,
        'daily_metrics': daily_metrics
    }
    
    with open('ml/prophet_models.pkl', 'wb') as f:
        pickle.dump(prophet_data, f)
    
    print(f"\nProphet models saved to ml/prophet_models.pkl")
    print(f"Trained models for: {list(models.keys())}")
    
    return prophet_data

def get_forecast_summary():
    """Get a summary of forecasts for dashboard display."""
    
    try:
        with open('ml/prophet_models.pkl', 'rb') as f:
            prophet_data = pickle.load(f)
        
        summary = {}
        for metric, forecast in prophet_data['forecasts'].items():
            # Get latest actual and predicted values
            latest_actual = prophet_data['daily_metrics'][metric].iloc[-1]
            latest_pred = forecast[metric].iloc[-1]
            
            # Calculate trend (7-day average)
            recent_actual = prophet_data['daily_metrics'][metric].tail(7).mean()
            recent_pred = forecast[metric].tail(7).mean()
            
            summary[metric] = {
                'current_value': latest_actual,
                'predicted_value': latest_pred,
                'trend': 'increasing' if recent_pred > recent_actual else 'decreasing',
                'change_percent': ((recent_pred - recent_actual) / recent_actual * 100) if recent_actual > 0 else 0
            }
        
        return summary
    
    except FileNotFoundError:
        print("Prophet models not found. Run train_prophet_models() first.")
        return {}

if __name__ == "__main__":
    train_prophet_models()
    print("\nForecast Summary:")
    print(get_forecast_summary()) 