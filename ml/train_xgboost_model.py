import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, classification_report
import pickle
import os

def train_xgboost_model():
    """Train XGBoost models for advanced regression and classification."""
    
    # Load unified data
    df = pd.read_csv('output/unified_campaign_data.csv')
    
    # Clean and prepare data
    df = df.dropna(subset=['clicks', 'impressions', 'spend'])
    
    # Calculate target variables
    df['ctr'] = df['clicks'] / df['impressions']
    df['cpa'] = df['spend'] / df['conversions'].fillna(1)
    df['roi'] = (df['revenue'] - df['spend']) / df['spend'] if 'revenue' in df.columns else 0
    
    # Binary classification: High performing campaigns (top 25%)
    df['high_performing'] = (df['ctr'] > df['ctr'].quantile(0.75)).astype(int)
    
    # Prepare features
    features = ['platform', 'spend', 'impressions']
    if 'demographic' in df.columns:
        features.append('demographic')
    if 'intent_score' in df.columns:
        features.append('intent_score')
    
    X = df[features].copy()
    y_ctr = df['ctr']
    y_high_perf = df['high_performing']
    
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
    
    # Train XGBoost regression model for CTR
    mask = np.isfinite(y_ctr)
    X_clean = X_final[mask]
    y_clean = y_ctr[mask]
    
    if len(X_clean) > 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X_clean, y_clean, test_size=0.2, random_state=42
        )
        
        # XGBoost Regression
        xgb_reg = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        xgb_reg.fit(X_train, y_train)
        
        y_pred = xgb_reg.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"XGBoost CTR Model - MSE: {mse:.4f}, R²: {r2:.4f}")
        
        # XGBoost Classification for high performing campaigns
        X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
            X_clean, y_high_perf[mask], test_size=0.2, random_state=42
        )
        
        xgb_clf = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        xgb_clf.fit(X_train_clf, y_train_clf)
        
        y_pred_clf = xgb_clf.predict(X_test_clf)
        print("\nXGBoost Classification Report (High Performing Campaigns):")
        print(classification_report(y_test_clf, y_pred_clf))
        
        # Save models
        xgb_models = {
            'regression': xgb_reg,
            'classification': xgb_clf,
            'label_encoders': {
                'platform': le_platform,
                'demographic': le_demo if 'demographic' in X.columns else None
            },
            'feature_cols': feature_cols,
            'metrics': {
                'regression': {'mse': mse, 'r2': r2}
            }
        }
        
        with open('ml/xgboost_models.pkl', 'wb') as f:
            pickle.dump(xgb_models, f)
        
        print("XGBoost models saved to ml/xgboost_models.pkl")
        return xgb_models

if __name__ == "__main__":
    train_xgboost_model() 