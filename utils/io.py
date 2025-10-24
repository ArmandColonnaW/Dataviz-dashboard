import os
import pandas as pd
import streamlit as st

# URL officielle du jeu de données IRVE consolidé (Etalab)
DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/eb76d20a-8501-400e-b336-d85724de5435"

@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    """
    Load the IRVE dataset directly from the official data.gouv.fr API link.

    - The file is downloaded and cached automatically (Streamlit handles it).
    - No manual upload or local file required.
    - Data is read directly into a pandas DataFrame.
    """
    try:
        st.info("Fetching dataset from data.gouv.fr...")
        df = pd.read_csv(DATA_URL, sep=",")
        st.success("Dataset successfully loaded from the online source.")
        return df

    except Exception as e:
        st.error("Failed to load dataset from the remote link.")
        st.exception(e)
        st.stop()
