import streamlit as st
import pandas as pd

from utils.io import load_data
from utils.prep import clean_irve_data

# Sections
from sections.intro import section_intro
from sections.overview import section_overview
from sections.deep_dives import section_deep_dives
from sections.conclusions import section_conclusion

st.set_page_config(
    page_title="EV Charging in France — Data Storytelling",
    layout="wide",
)

# =========================
# DATA LOADING
# =========================
st.sidebar.header("Dataset loading")
st.sidebar.caption("The file is automatically loaded from /data/.")

with st.spinner("Loading the IRVE dataset..."):
    df_raw = load_data()
st.sidebar.success("Dataset loaded successfully.")

# --- Display quick dataset info before cleaning
st.sidebar.markdown("### Dataset info (raw)")
st.sidebar.write(f"Rows: {len(df_raw):,}")
st.sidebar.write(f"Columns: {len(df_raw.columns)}")

# =========================
# DATA CLEANING (visible storytelling)
# =========================
st.subheader("Data Cleaning — making the dataset analysis-ready")
st.write(
    """
    Raw open data often contains **duplicates, missing coordinates, or inconsistent formats**.  
    Cleaning ensures we tell a *truthful and reliable* story.
    Here’s what we fix before any visualization:
    """
)
st.markdown(
    """
    - Normalize column names  
    - Convert service dates to real datetime format  
    - Remove rows without valid latitude/longitude  
    - Standardize and group power ratings (Normal, Fast, Very fast, Ultra-fast)  
    - Remove duplicate charge points (`id_pdc_itinerance`, `id_pdc_local`)  
    """
)

with st.spinner("Cleaning and preparing data..."):
    df = clean_irve_data(df_raw)

# Compare before/after
col1, col2 = st.columns(2)
with col1:
    st.metric("Rows before cleaning", f"{len(df_raw):,}")
with col2:
    st.metric("Rows after cleaning", f"{len(df):,}")
missing_before = df_raw.isna().mean().mean() * 100
missing_after = df.isna().mean().mean() * 100
st.caption(f"Average missing values reduced from **{missing_before:.1f}%** to **{missing_after:.1f}%** after cleaning.")

st.divider()

# =========================
# MAIN SECTIONS
# =========================
section_intro()
st.divider()
section_overview(df, df_raw)
st.divider()
section_deep_dives(df)
st.divider()
section_conclusion(df_raw)

st.caption("© Student project — IRVE Data Storytelling — Streamlit")
