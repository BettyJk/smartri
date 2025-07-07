import numpy as np

# Country risk mapping
COUNTRY_RISK = {"Chine": 5, "Espagne": 3, "France": 2, "Maroc": 1}

# Weights for risk score
WEIGHTS = {
    'days_since_RI': 0.5,
    'country_risk': 2.0,
    'SGR_count': 1.0,
    'days_until_end_series': -0.2
}

# Thresholds for classification
THRESHOLDS = {
    'Urgent': 80,
    'Normal': 40
}

def compute_risk_score(row):
    score = 0
    score += WEIGHTS['days_since_RI'] * min(row['days_since_RI'], 9999)
    score += WEIGHTS['country_risk'] * row['country_risk']
    score += WEIGHTS['SGR_count'] * row['SGR_count']
    score += WEIGHTS['days_until_end_series'] * max(row['days_until_end_series'], -9999)
    if np.isnan(row['days_since_RI']) or row['days_since_RI'] >= 9999:
        score += 100  # High penalty for missing RI
    return score

def classify_risk(score):
    if score >= THRESHOLDS['Urgent']:
        return 'Urgent'
    elif score >= THRESHOLDS['Normal']:
        return 'Normal'
    else:
        return 'Safe'
