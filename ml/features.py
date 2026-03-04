import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class LogFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Custom transformer to extract features from raw log dictionaries/DataFrames.
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        # Expecting X to be a DataFrame
        X_copy = X.copy()
        
        # 1. Temporal Features
        # Assuming 'timestamp' is in specific format or needs parsing
        if 'timestamp' in X_copy.columns:
            X_copy['timestamp'] = pd.to_datetime(X_copy['timestamp'])
            X_copy['hour'] = X_copy['timestamp'].dt.hour
            X_copy['day_of_week'] = X_copy['timestamp'].dt.dayofweek
        else:
            X_copy['hour'] = 0
            X_copy['day_of_week'] = 0

        # 2. Network Features
        # Fill missing ports with -1 (common in non-network logs)
        X_copy['src_port'] = pd.to_numeric(X_copy['src_port'], errors='coerce').fillna(-1).astype(int)
        X_copy['dst_port'] = pd.to_numeric(X_copy['dst_port'], errors='coerce').fillna(-1).astype(int)
        
        # 3. Rare Categories Handling (simple version)
        # We will handle categorical encoding in the main pipeline
        
        return X_copy[['hour', 'day_of_week', 'src_port', 'dst_port', 'rule_id', 'action']]

def create_preprocessor():
    """
    Returns a Sklearn ColumnTransformer for the pipeline.
    """
    categorical_features = ['rule_id', 'action']
    numerical_features = ['hour', 'day_of_week', 'src_port', 'dst_port']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ]
    )
    
    return preprocessor
