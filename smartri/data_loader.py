import pandas as pd
from typing import Tuple

def load_inventory_data(filepath: str) -> pd.DataFrame:
    """
    Load inventory data from Excel, parse relevant date columns.
    """
    date_cols = [
        'Date fin série',
        'Date transfert série',
        'Date dernier RI'
    ]
    df = pd.read_excel(filepath, parse_dates=date_cols, engine='openpyxl')
    return df
