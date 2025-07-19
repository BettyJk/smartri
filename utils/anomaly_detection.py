import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(df, features=None, contamination=0.05, random_state=42):
    """
    Detect anomalies in the given DataFrame using IsolationForest.
    Args:
        df: pandas DataFrame with inventory data
        features: list of column names to use for detection
        contamination: expected proportion of outliers
        random_state: random seed
    Returns:
        DataFrame with an 'anomaly' column (-1: anomaly, 1: normal)
    """
    if features is None:
        # Default to common numeric fields if not specified
        features = [col for col in df.columns if df[col].dtype in ['float64', 'int64']]
    X = df[features].dropna()
    model = IsolationForest(contamination=contamination, random_state=random_state)
    df['anomaly'] = 1
    df.loc[X.index, 'anomaly'] = model.fit_predict(X)
    return df
