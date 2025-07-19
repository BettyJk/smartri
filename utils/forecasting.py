import pandas as pd
from prophet import Prophet

def forecast_quantity(df, produit_col="Produit", date_col="Date du dernier RI", qty_col="Quantité", periods=12):
    """
    For each product, forecast future quantity using Prophet.
    Returns a dict: {produit: forecast_df}
    """
    results = {}
    skipped = []
    for produit, group in df.groupby(produit_col):
        # Prepare data for Prophet
        data = group[[date_col, qty_col]].copy()
        data = data.rename(columns={date_col: "ds", qty_col: "y"})
        # Try to convert numeric 'ds' to dates if needed
        if data["ds"].dtype in [int, float] or data["ds"].apply(lambda x: isinstance(x, (int, float))).all():
            # Assume numbers are days since a reference date (e.g., 1900-01-01)
            ref_date = pd.Timestamp("1900-01-01")
            data["ds"] = pd.to_numeric(data["ds"], errors='coerce')
            data["ds"] = data["ds"].apply(lambda x: ref_date + pd.Timedelta(days=x) if pd.notnull(x) else pd.NaT)
        else:
            data["ds"] = pd.to_datetime(data["ds"], errors='coerce')
        data = data.dropna(subset=["ds", "y"])
        if len(data) < 2:
            skipped.append((produit, "Not enough valid date/quantity values"))
            continue
        try:
            model = Prophet()
            model.fit(data)
            future = model.make_future_dataframe(periods=periods, freq='M')
            forecast = model.predict(future)
            results[produit] = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
        except Exception as e:
            skipped.append((produit, str(e)))
    return results, skipped
