# --- New function: enrich_and_score_dataframe
import copy
import numpy as np
def enrich_and_score_dataframe(input_df):
    """
    For each row in input_df, find the corresponding entry in reference_data (by 'Produit'),
    fill in missing columns from the reference, and score using critere.json.
    Returns a new DataFrame with scores and categories.
    """
    try:
        # Ensure input DataFrame has unique column names and remove duplicates
        input_df = input_df.copy()
        # Remove duplicate columns by keeping only the first occurrence (pandas-native)
        input_df = input_df.loc[:, ~input_df.columns.duplicated()]
        # Deduplicate column names (add suffixes if needed)
        input_df.columns = pd.io.parsers.ParserBase({'names': input_df.columns})._maybe_dedup_names(input_df.columns)
        required_cols = [
            "Type d'emballage",
            "Flux Pièce",
            "Date du dernier RI",
            "Prix Pièce",
            "ECV/COR",
            "UC"
        ]
        enriched_rows = []
        for idx, row in input_df.iterrows():
            produit = str(row.get("Produit", "")).strip()
            # Start with a copy of the input row
            enriched = copy.deepcopy(row.to_dict())
            # If product exists in reference, fill missing columns
            ref = json_index.get(produit)
            if ref:
                for col in required_cols:
                    if (col not in enriched or pd.isna(enriched.get(col))) and (ref.get(col, None) is not None):
                        enriched[col] = ref.get(col, None)
            # Remove duplicate keys if any (shouldn't happen, but for safety)
            enriched = {k: v for k, v in enriched.items()}
            enriched_rows.append(enriched)
        enriched_df = pd.DataFrame(enriched_rows)
        # Force unique column names by appending suffixes to duplicates
        enriched_df.columns = pd.io.parsers.ParserBase({'names': enriched_df.columns})._maybe_dedup_names(enriched_df.columns)
        # Force unique index
        enriched_df = enriched_df.reset_index(drop=True)
        # Score the enriched DataFrame
        return calculate_scores(enriched_df)
    except Exception as e:
        print(f"Erreur lors du mapping ou de l'enrichissement : {e}")
        # Return a DataFrame with error columns so the app doesn't crash
        error_df = input_df.copy()
        error_df["Score Calculé"] = "Erreur"
        error_df["Catégorie"] = "Erreur"
        return error_df
import json
import pandas as pd
import re
from datetime import datetime

# Charger les critères de pondération (fallback)
with open("data/critere.json", encoding="utf-8") as f:
    criteria = json.load(f)

# Charger la base de données des produits scorés
with open("data/Planning_Inventaire_Integral_clean.json", encoding="utf-8") as f:
    reference_data = json.load(f)

# Indexer le JSON par produit
json_index = {item["Produit"]: item for item in reference_data}

# --- Parse interval rules like "37 à 72 Jours", "< 20", ">=516 & <688"
def parse_interval(condition):
    condition = condition.strip()

    if ">=" in condition and "<" in condition and "&" in condition:
        match = re.findall(r"\d+", condition)
        if len(match) == 2:
            a, b = map(float, match)
            return lambda v: float(a) <= float(v) < float(b)

    if "à" in condition:
        match = re.findall(r"\d+", condition)
        if len(match) == 2:
            a, b = map(float, match)
            return lambda v: a <= float(v) <= b

    if condition.startswith(">="):
        match = re.findall(r"\d+", condition)
        if match:
            return lambda v: float(v) >= float(match[0])

    if condition.startswith("<"):
        match = re.findall(r"\d+", condition)
        if match:
            return lambda v: float(v) < float(match[0])

    if condition.startswith(">"):
        match = re.findall(r"\d+", condition)
        if match:
            return lambda v: float(v) > float(match[0])

    return lambda v: str(v).strip().lower() == condition.strip().lower()


def get_pond_and_coeff(value, critere):
    for c in criteria:
        if c["Critère"] == critere:
            for spec in c["Spécifications"]:
                try:
                    if parse_interval(spec["Spécification"])(value):
                        return spec["Pondération"], c["Coefficient"]
                except:
                    continue
    return 0, 0


def calculate_scores(df):
    scores = []
    categories = []
    statuts = []
    today = pd.Timestamp(datetime.today().date())

    for idx, row in df.iterrows():
        total = 0
        debug_info = []
        for c in criteria:
            crit = c["Critère"]
            if crit in row and pd.notna(row[crit]):
                value = row[crit]

                # Si le critère est une date → convertir en nombre de jours
                if crit == "Date du dernier RI":
                    try:
                        delta = (today - pd.to_datetime(value)).days
                        value = delta
                    except Exception as e:
                        debug_info.append(f"[Row {idx}] Failed to parse date for '{crit}': {value} ({e})")
                        value = 0

                pond, coeff = get_pond_and_coeff(value, crit)
                debug_info.append(f"[Row {idx}] Critère: {crit}, Value: {value}, Pondération: {pond}, Coefficient: {coeff}, Contribution: {pond * coeff}")
                total += pond * coeff
            else:
                debug_info.append(f"[Row {idx}] Critère: {crit} not found or NaN in row.")

        print(f"[Row {idx}] Total Score: {total}")
        for info in debug_info:
            print(info)

        scores.append(round(total, 2))
        # Catégorie
        if total >= 16:
            categories.append("Haut")
        elif total >= 13:
            categories.append("Moyen")
        elif total > 0:
            categories.append("Bas")
        else:
            categories.append("Non pondéré")
        # Statut Inventaire
        if total <= 10:
            statuts.append("Urgent")
        elif total < 16:
            statuts.append("Normal")
        else:
            statuts.append("Safe")

    df["Score Calculé"] = scores
    df["Catégorie"] = categories
    df["Statut Inventaire"] = statuts
    return df


# --- Fonction principale utilisée par l’app
def enrich_with_existing_scores(df):
    scores = []
    categories = []

    statuts = []
    for _, row in df.iterrows():
        produit = str(row.get("Produit", "")).strip()
        if produit in json_index:
            data = json_index[produit]
            score_val = data.get("Score total", 0)
            cat_val = data.get("Catégorie", "Non pondéré")
        else:
            fallback = calculate_scores(pd.DataFrame([row.copy()]))
            score_val = fallback["Score Calculé"].iloc[0]
            cat_val = fallback["Catégorie"].iloc[0]
        scores.append(score_val)
        categories.append(cat_val)
        # Always compute status from score
        if score_val <= 10:
            statuts.append("Urgent")
        elif score_val < 16:
            statuts.append("Normal")
        else:
            statuts.append("Safe")
    df["Score Calculé"] = scores
    df["Catégorie"] = categories
    df["Statut Inventaire"] = statuts
    return df
