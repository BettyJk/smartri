import pandas as pd
import numpy as np
from datetime import datetime
from utils import compute_risk_score, classify_risk

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    today = pd.Timestamp.today().normalize()
    df['days_since_RI'] = (today - df['Date dernier RI']).dt.days
    df['days_since_RI'] = df['days_since_RI'].fillna(9999)  # High value for missing
    df['days_until_end_series'] = (df['Date fin série'] - today).dt.days
    df['days_until_end_series'] = df['days_until_end_series'].fillna(-9999)
    df['SGR_count'] = df['SGR/Ligne'].astype(str).apply(lambda x: len(str(x).split(',')))
    df['country_risk'] = df['Pays'].map({"Chine": 5, "Espagne": 3, "France": 2, "Maroc": 1}).fillna(3)
    df['risk_score'] = df.apply(compute_risk_score, axis=1)
    df['risk_level'] = df['risk_score'].apply(classify_risk)
    return df
