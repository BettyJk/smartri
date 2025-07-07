import streamlit as st
import pandas as pd
from data_loader import load_inventory_data
from feature_engineering import add_features
from datetime import datetime

st.set_page_config(page_title="SmartRI: Inventory Audit Prioritization", layout="wide")
st.image("logo.png", width=200)
st.markdown("### Plateforme d’audit inventaire priorisé pour Stellantis")
st.title("SmartRI: AI-Powered Prioritized Inventory Audit System")

# File uploader for user data
uploaded_file = st.file_uploader("Téléchargez votre fichier Excel d'inventaire", type=["xlsx"])
if uploaded_file is not None:
    with st.spinner('Analyse en cours...'):
        df = load_inventory_data(uploaded_file)
        df = add_features(df)
else:
    st.info("Veuillez télécharger un fichier Excel pour commencer.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("Filtres avancés")
    country = st.multiselect("Pays", options=sorted(df['Pays'].dropna().unique()), default=None)
    supplier = st.multiselect("Vendeur", options=sorted(df['Vendeur'].dropna().unique()), default=None)
    risk_level = st.multiselect("Niveau de risque", options=["Urgent", "Normal", "Safe"], default=None)
    date_min = st.date_input("Date RI min", value=None)
    date_max = st.date_input("Date RI max", value=None)

# Filtering logic
filtered = df.copy()
if country:
    filtered = filtered[filtered['Pays'].isin(country)]
if supplier:
    filtered = filtered[filtered['Vendeur'].isin(supplier)]
if risk_level:
    filtered = filtered[filtered['risk_level'].isin(risk_level)]
if date_min:
    filtered = filtered[filtered['Date dernier RI'] >= pd.to_datetime(date_min)]
if date_max:
    filtered = filtered[filtered['Date dernier RI'] <= pd.to_datetime(date_max)]

# Color map for risk
def color_risk(val):
    if val == 'Urgent':
        return 'background-color: #ff4d4d; color: white;'
    elif val == 'Normal':
        return 'background-color: #ffe066; color: black;'
    else:
        return 'background-color: #d4edda; color: black;'

# Show table
st.subheader("Inventaire priorisé")
st.dataframe(filtered.style.applymap(color_risk, subset=['risk_level']), use_container_width=True)

# Export
st.download_button(
    label="Exporter en CSV",
    data=filtered.to_csv(index=False).encode('utf-8'),
    file_name=f"SmartRI_export_{datetime.now().date()}.csv",
    mime='text/csv'
)

# Top risky items
st.subheader("Top 10 Risques Urgents")
top_urgent = filtered[filtered['risk_level'] == 'Urgent'].sort_values('risk_score', ascending=False).head(10)
st.table(top_urgent[['Produit', 'Désignation', 'Vendeur', 'Pays', 'risk_score', 'risk_level', 'Date dernier RI']])

# Bonus: Daily summary report
if st.button("Générer rapport journalier (Markdown)"):
    urgent_count = (filtered['risk_level'] == 'Urgent').sum()
    normal_count = (filtered['risk_level'] == 'Normal').sum()
    safe_count = (filtered['risk_level'] == 'Safe').sum()
    report = f"""
# Rapport Journalier SmartRI ({datetime.now().date()})

- **Total entrées**: {len(filtered)}
- **Urgent**: {urgent_count}
- **Normal**: {normal_count}
- **Safe**: {safe_count}

## Top 5 Urgents
"""
    report += top_urgent.head(5).to_markdown(index=False)
    st.markdown(report)
