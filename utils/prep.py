import pandas as pd
import numpy as np

def clean_irve_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare the IRVE dataset for analysis/visualization.

    This function applies a series of data quality improvements
    to make the dataset reliable for storytelling and mapping.
    Each step has a rationale: transparency, consistency, and usability.
    """

    # --- 1. Work on a copy to avoid modifying the original dataset in memory ---
    df = df.copy()

    # --- 2. Standardize column names (lowercase, no extra spaces) ---
    # Why: column names differ across data sources; cleaning them makes
    # code robust and easier to reuse in merges or visualizations.
    df.columns = df.columns.str.strip().str.lower()

    # --- 3. Convert the installation date to datetime + extract year ---
    # Why: dates are often stored as text, but to plot time trends,
    # we need real datetime objects. The year helps group and filter easily.
    if "date_mise_en_service" in df.columns:
        df["date_mise_en_service"] = pd.to_datetime(df["date_mise_en_service"], errors="coerce")
        df["annee_mise_en_service"] = df["date_mise_en_service"].dt.year

    # --- 4. Ensure latitude/longitude are numeric ---
    # Why: these values sometimes come as strings or malformed numbers.
    # We coerce to numeric so the map doesn’t break and filters work correctly.
    for col in ["consolidated_latitude", "consolidated_longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- 5. Standardize charging power and classify it into categories ---
    # Why: the dataset contains numeric power values (kW),
    # but grouping them into human-readable categories helps storytelling
    # (“Normal”, “Fast”, “Ultra-fast”) and consistent color-coding on visuals.
    if "puissance_nominale" in df.columns:
        # Convert to numeric to avoid text errors (e.g., "22 kW" → 22)
        df["puissance_nominale"] = pd.to_numeric(df["puissance_nominale"], errors="coerce")

        # Define bins and labels based on charging speed
        bins = [0, 22, 50, 150, 1000]
        labels = ["Normal (<22kW)", "Fast (22–50kW)", "Very fast (50–150kW)", "Ultra-fast (>150kW)"]
        df["categorie_puissance"] = pd.cut(
            df["puissance_nominale"], bins=bins, labels=labels, right=False
        )

    # --- 6. Clean key text fields (operator, municipality names) ---
    # Why: inconsistent capitalization (“TOTALENERGIES”, “Total energies”)
    # creates duplicates in aggregations. We unify to title case for readability.
    for col in ["nom_amenageur", "nom_operateur", "nom_commune"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title().str.strip()

    # --- 7. Drop duplicates based on unique identifiers ---
    # Why: some charge points appear twice in the open dataset
    # (e.g., local vs itinerant IDs). Keeping one prevents double-counting.
    keys = [k for k in ["id_pdc_itinerance", "id_pdc_local"] if k in df.columns]
    if keys:
        df = df.drop_duplicates(subset=keys, keep="first")

    # --- 8. Remove rows with missing coordinates ---
    # Why: mapping functions (pydeck, folium) crash if lat/lon are null.
    # These rows can’t appear on a map, so we remove them safely.
    if {"consolidated_latitude", "consolidated_longitude"}.issubset(df.columns):
        df = df.dropna(subset=["consolidated_latitude", "consolidated_longitude"])

    # --- 9. Keep only relevant columns for the dashboard ---
    # Why: reduces memory use and makes caching faster.
    # Keeps only columns needed for KPIs, filters, and visualizations.
    keep = [
        "nom_amenageur", "nom_operateur", "nom_commune",
        "consolidated_latitude", "consolidated_longitude",
        "puissance_nominale", "categorie_puissance",
        "date_mise_en_service", "annee_mise_en_service",
    ]
    keep = [c for c in keep if c in df.columns]

    # --- 10. Return a clean, compact DataFrame ready for visualizations ---
    return df[keep].copy()
