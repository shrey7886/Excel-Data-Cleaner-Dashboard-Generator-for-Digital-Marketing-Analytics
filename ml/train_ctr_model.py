import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os

def train_ctr_model():
    """Train a Random Forest model to predict CTR, ROI, and CPA."""
    
    # Load unified data
    df = pd.read_csv('output/unified_campaign_data.csv')
    
    # Clean and prepare data
    df = df.dropna(subset=['clicks', 'impressions', 'spend'])
    
    # Calculate target variables
    df['ctr'] = df['clicks'] / df['impressions']
    df['cpa'] = df['spend'] / df['conversions'].fillna(1)
    df['roi'] = (df['revenue'] - df['spend']) / df['spend'] if 'revenue' in df.columns else 0
    
    # Prepare features
    features = ['platform', 'spend', 'impressions']
    if 'demographic' in df.columns:
        features.append('demographic')
    if 'intent_score' in df.columns:
        features.append('intent_score')
    
    X = df[features].copy()
    y_ctr = df['ctr']
    y_cpa = df['cpa']
    y_roi = df['roi']
    
    # Encode categorical variables
    le_platform = LabelEncoder()
    X['platform_encoded'] = le_platform.fit_transform(X['platform'])
    
    if 'demographic' in X.columns:
        le_demo = LabelEncoder()
        X['demographic_encoded'] = le_demo.fit_transform(X['demographic'].fillna('Unknown'))
    
    # Select final features
    feature_cols = ['platform_encoded', 'spend', 'impressions']
    if 'demographic_encoded' in X.columns:
        feature_cols.append('demographic_encoded')
    if 'intent_score' in X.columns:
        feature_cols.append('intent_score')
    
    X_final = X[feature_cols]
    
    # Train models
    models = {}
    metrics = {}
    
    for target_name, y in [('ctr', y_ctr), ('cpa', y_cpa), ('roi', y_roi)]:
        # Remove infinite values
        mask = np.isfinite(y)
        X_clean = X_final[mask]
        y_clean = y[mask]
        
        if len(X_clean) > 10:  # Only train if we have enough data
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y_clean, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            models[target_name] = model
            metrics[target_name] = {'mse': mse, 'r2': r2}
            
            print(f"{target_name.upper()} Model - MSE: {mse:.4f}, R²: {r2:.4f}")
    
    # Save models and encoders
    model_data = {
        'models': models,
        'label_encoders': {
            'platform': le_platform,
            'demographic': le_demo if 'demographic' in X.columns else None
        },
        'feature_cols': feature_cols,
        'metrics': metrics
    }
    
    with open('ml/trained_models.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Models saved to ml/trained_models.pkl")
    return model_data

if __name__ == "__main__":
    train_ctr_model() 