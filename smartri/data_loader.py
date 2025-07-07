import pandas as pd
from typing import Tuple
import streamlit as st

def get_excel_columns(uploaded_file):
    # Read only the header to get columns
    return pd.read_excel(uploaded_file, nrows=0, engine='openpyxl').columns.tolist()

@st.cache_data(show_spinner=False)
def load_inventory_data(filepath: str) -> pd.DataFrame:
    """
    Load inventory data from Excel, parse relevant date columns, only necessary columns.
    """
    date_cols = [
        'Date fin série',
        'Date transfert série',
        'Date dernier RI'
    ]
    usecols = [
        'Produit', 'Désignation', 'Vendeur', 'Raison sociale du vendeur',
        'Expéditeur', 'Pays', "Raison sociale de l'expéditeur", 'Identifiant appro',
        'SGR/Ligne', 'Date fin série', 'Date transfert série', 'Date dernier RI'
    ]
    df = pd.read_excel(filepath, parse_dates=date_cols, usecols=usecols, engine='openpyxl')
    return df
