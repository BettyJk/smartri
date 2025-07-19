
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.mapper import map_columns, infer_flux_pays
from utils.scorer import enrich_with_existing_scores, json_index
from utils.file_utils import convert_df_to_excel
from utils.forecasting import forecast_quantity

st.set_page_config(page_title="AI - Planification d’Inventaire", layout="wide")
st.title("📦 Outil IA de Planification d’Inventaire")


@st.cache_data(show_spinner=False)
def load_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df.reset_index(drop=True)  # Ensure a unique, simple index
    return df

@st.cache_data(show_spinner=False)
def map_and_enrich(df):
    df_mapped = map_columns(df)
    # Ensure unique columns and index after mapping
    df_mapped = df_mapped.loc[:, ~df_mapped.columns.duplicated()]
    df_mapped = df_mapped.reset_index(drop=True)
    if "Pays" in df_mapped.columns:
        df_mapped["Flux Pièce"] = df_mapped["Pays"].apply(infer_flux_pays)
    df_final = enrich_with_existing_scores(df_mapped)
    return df_mapped, df_final

uploaded_file = st.file_uploader("📤 Importer un fichier Excel", type=["xlsx"])



if uploaded_file:

    if not uploaded_file:
        st.info("Veuillez importer un fichier Excel contenant au moins 2 dates valides et quantités par produit pour activer la prévision.")
        st.stop()
    try:
        df = load_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        st.stop()

    st.subheader("🔍 Aperçu du fichier importé")
    st.dataframe(df.head(20))

    try:
        df_mapped, df_final = map_and_enrich(df)
    except Exception as e:
        st.error(f"Erreur lors du mapping ou de l'enrichissement : {e}")
        st.stop()

    # --- Sidebar Filtering ---
    st.sidebar.header("🔎 Filtres")
    filter_df = df_final.copy()
    # Filter by Produit
    if "Produit" in filter_df.columns:
        produits = filter_df["Produit"].dropna().unique().tolist()
        selected_produits = st.sidebar.multiselect("Produit", produits)
        if selected_produits:
            filter_df = filter_df[filter_df["Produit"].isin(selected_produits)]
    # Filter by Pays
    if "Pays" in filter_df.columns:
        pays = filter_df["Pays"].dropna().unique().tolist()
        selected_pays = st.sidebar.multiselect("Pays", pays)
        if selected_pays:
            filter_df = filter_df[filter_df["Pays"].isin(selected_pays)]
    # Filter by Catégorie
    if "Catégorie" in filter_df.columns:
        categories = filter_df["Catégorie"].dropna().unique().tolist()
        selected_categories = st.sidebar.multiselect("Catégorie", categories)
        if selected_categories:
            filter_df = filter_df[filter_df["Catégorie"].isin(selected_categories)]
    # Filter by Date du dernier RI (as a date range)
    if "Date du dernier RI" in filter_df.columns:
        try:
            filter_df["Date du dernier RI"] = pd.to_datetime(filter_df["Date du dernier RI"], errors='coerce')
            min_date = filter_df["Date du dernier RI"].min()
            max_date = filter_df["Date du dernier RI"].max()
            date_range = st.sidebar.date_input("Date du dernier RI (plage)", [min_date, max_date])
            if len(date_range) == 2:
                filter_df = filter_df[(filter_df["Date du dernier RI"] >= pd.to_datetime(date_range[0])) & (filter_df["Date du dernier RI"] <= pd.to_datetime(date_range[1]))]
        except Exception:
            pass

    # --- Dashboard Summary ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total produits", len(df_final))
    with col2:
        st.metric("Références manquantes", sum([str(row.get('Produit', '')).strip() not in json_index for _, row in df_mapped.iterrows()]))
    with col3:
        st.metric("Colonnes", len(df_final.columns))
    with col4:
        st.metric("Valeurs manquantes", int(df_final.isna().sum().sum()))

    st.success("✅ Résultat enrichi avec score intelligent")
    st.dataframe(filter_df.head(50))

    # Anomaly Detection Option
    st.subheader("🔎 Détection d'anomalies (AI)")
    if st.button("Détecter les anomalies dans les données"):
        from utils.anomaly_detection import detect_anomalies
        features = [col for col in ["Quantité", "Prix Pièce", "UC"] if col in df_final.columns]
        if not features:
            st.warning("Aucune colonne numérique pertinente trouvée pour la détection d'anomalies.")
        else:
            try:
                df_anom = detect_anomalies(df_final, features=features)
                n_anom = (df_anom['anomaly'] == -1).sum()
                st.info(f"{n_anom} anomalie(s) détectée(s) sur {len(df_anom)} lignes.")
                st.dataframe(df_anom[df_anom['anomaly'] == -1].head(50))

                # Show distribution and anomaly graphs
                for feat in features:
                    fig, ax = plt.subplots()
                    sns.histplot(df_anom[feat], kde=True, color='blue', label='Normal', ax=ax)
                    if (df_anom['anomaly'] == -1).any():
                        sns.histplot(df_anom[df_anom['anomaly'] == -1][feat], color='red', label='Anomalie', ax=ax)
                    ax.set_title(f"Distribution de {feat} (anomalies en rouge)")
                    ax.legend()
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Erreur lors de la détection d'anomalies : {e}")

    # Add Reference Button for missing products
    missing_refs = [idx for idx, row in df_mapped.iterrows() if str(row.get("Produit", "")).strip() and str(row.get("Produit", "")).strip() not in json_index]

    if missing_refs:
        st.warning(f"{len(missing_refs)} référence(s) non trouvée(s) dans la base de données.")
        st.markdown("**Détails des références manquantes :**")
        st.dataframe(df_mapped.loc[missing_refs].head(20))
        if st.button("Ajouter les références manquantes dans la base JSON"):
            from utils.add_reference import add_reference
            added = 0
            for idx in missing_refs:
                row = df_mapped.loc[idx].to_dict()
                for k, v in row.items():
                    if pd.isna(v):
                        row[k] = ""
                try:
                    add_reference(row)
                    added += 1
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout de la référence : {e}")
            st.success(f"{added} référence(s) ajoutée(s) à la base JSON.")

    excel_bytes = convert_df_to_excel(df_final)
    st.download_button(
        label="📥 Télécharger Résultat Excel",
        data=excel_bytes,
        file_name="résultat_inventaire.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Forecasting Feature ---
    st.subheader("📈 Prévision de la demande (AI)")
    if st.button("Lancer la prévision de la demande (Prophet)"):
        try:
            # Use only products with enough data
            results, skipped = forecast_quantity(df_final)
            if not results:
                st.info("Pas assez de données pour la prévision.")
            else:
                for produit, forecast in results.items():
                    st.markdown(f"**Prévision pour {produit}:**")
                    st.write(f"Shape: {forecast.shape}, Columns: {forecast.columns.tolist()}")
                    st.dataframe(forecast.head(24))
                    st.line_chart(forecast.set_index("ds")["yhat"])
            if skipped:
                st.warning(f"Produits ignorés pour la prévision:")
                for produit, reason in skipped:
                    st.write(f"- {produit}: {reason}")
        except Exception as e:
            st.error(f"Erreur lors de la prévision : {e}")
