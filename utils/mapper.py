def map_columns(df):
    rename_map = {
        "Date fin série": "Date du dernier RI",
        "Date dernier RI": "Date du dernier RI",
        "Rebut Quantité": "Rebut",
        "UC": "UC",
        "Prix Pièce": "Prix Pièce",
        "Pays": "Pays",
        "Raison sociale de l'expéditeur": "Fournisseur",
        # Quantity column mappings
        "Qte": "Quantité",
        "Qté": "Quantité",
        "quantite": "Quantité",
        "Quantite": "Quantité",
        "QUANTITE": "Quantité",
        "QUANTITY": "Quantité",
        "Quantity": "Quantité",
    }
    df = df.rename(columns=rename_map)
    # Ensure 'Quantité' column always exists
    if "Quantité" not in df.columns:
        df["Quantité"] = 0

    # Ajouter colonnes manquantes pour le fallback
    if "Prix Pièce" not in df.columns:
        df["Prix Pièce"] = 1.0
    if "UC" not in df.columns:
        df["UC"] = 100
    if "Rebut" not in df.columns:
        df["Rebut"] = 0
    if "ECV/COR" not in df.columns:
        df["ECV/COR"] = 2
    if "Type d'emballage" not in df.columns:
        df["Type d'emballage"] = "GV"
    if "Pièces en suspicion de vol" not in df.columns:
        df["Pièces en suspicion de vol"] = "Non"
    if "Produit" not in df.columns:
        df["Produit"] = df.get("Libellé pièce", "Inconnu")

    # Automatically add 'Flux Pièce' using 'Pays' if not present
    if "Flux Pièce" not in df.columns:
        df["Flux Pièce"] = df["Pays"].apply(infer_flux_pays)
    return df

def infer_flux_pays(pays):
    if not isinstance(pays, str):
        return "Local"
    p = pays.lower()
    if p in ["france", "allemagne", "italie", "belgique"]:
        return "Europe Ouest &Central"
    elif p in ["espagne", "portugal"]:
        return "Ibérique"
    elif p in ["pologne", "hongrie", "roumanie"]:
        return "PECO"
    elif p in ["chine", "usa", "mexique", "turquie"]:
        return "Overseas"
    return "Local"
