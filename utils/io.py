import os
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    """
    Automatically loads the IRVE CSV file located in the /data folder.
    No other loading method is allowed.
    """
    csv_path = "data/consolidation-etalab-schema-irve-statique-v-2.3.1-20251024.csv"

    if not os.path.exists(csv_path):
        st.error(f"File not found: {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path)
    return df
