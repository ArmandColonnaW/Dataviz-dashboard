import streamlit as st
import pandas as pd
from utils.viz import map_irve_points, line_installations_over_time

def _nice_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except Exception:
        return str(n)

def section_overview(df: pd.DataFrame, df_raw: pd.DataFrame):
    st.header("1️ Overview — the big picture")

    st.markdown("**Story goal:** Establish the current scale, where points are, and how fast deployments are moving.")
    st.info("Why start here? A good story answers how big, where, and how it’s changing before any deep dive.")

    # ===== KPIs (tied to cleaned, filtered data) =====
    total_points = len(df)
    median_kw = df["puissance_nominale"].median() if "puissance_nominale" in df.columns and df["puissance_nominale"].notna().any() else None
    ultra_share = ((df["categorie_puissance"] == "Ultra-fast (>150kW)").mean() * 100) if "categorie_puissance" in df.columns and df["categorie_puissance"].notna().any() else None

    c1, c2, c3 = st.columns(3)
    c1.metric("Charging points (current view)", _nice_int(total_points))
    if median_kw is not None:
        c2.metric("Median power (kW)", f"{median_kw:.1f}")
    if ultra_share is not None:
        c3.metric("Share >150 kW", f"{ultra_share:.1f} %")

    st.caption("These KPIs answer: How big is the network? How fast can I typically charge? Is ultra-fast deployment significant?")

    # ===== Map (LOCAL filters — no communes) =====
    st.subheader("Where are the points?")
    st.write("We use a map because infrastructure is inherently geographic: corridors, clusters, and deserts become visible at a glance.")

    with st.expander("Map filters (local)"):
        cat_vals = df["categorie_puissance"].dropna().unique() if "categorie_puissance" in df.columns else []
        cats_sel = st.multiselect("Power categories (local)", cat_vals)
        pwr_min_map = st.slider(
            "Minimum power (kW, local)",
            float(df["puissance_nominale"].min()) if "puissance_nominale" in df.columns else 0.0,
            float(df["puissance_nominale"].max()) if "puissance_nominale" in df.columns else 350.0,
            float(df["puissance_nominale"].min()) if "puissance_nominale" in df.columns else 0.0,
        )

    df_map = df.copy()
    if len(cats_sel) > 0 and "categorie_puissance" in df_map.columns:
        df_map = df_map[df_map["categorie_puissance"].isin(cats_sel)]
    if "puissance_nominale" in df_map.columns:
        df_map = df_map[df_map["puissance_nominale"].fillna(0) >= pwr_min_map]

    st.pydeck_chart(
    map_irve_points(
        df_map,
        tooltip_cols=[c for c in ["nom_operateur", "nom_amenageur", "nom_commune"] if c in df_map.columns],
    ),
    use_container_width=True,
)

    st.markdown(
        """
        **What we can observe:**
        - Most ultra-fast charging points are clustered around major highways and metropolitan areas : Paris, Lyon, Marseille, Lille, and Bordeaux.
        - The western and central parts of France are denser, showing stronger deployment around key transport corridors.
        - Fewer stations appear in rural or mountainous regions (Massif Central, Alps, parts of Corsica), highlighting potential coverage gaps.
        - Border regions like Belgium and Germany also show high density suggesting cross-border interoperability and regional cooperation.

        This spatial pattern tells a clear story: France's charging network is no longer urban-only, it’s expanding along national roads and intercity routes, paving the way for long-distance EV travel.
        """
    )

    st.caption("Why it matters: location drives accessibility and equity. Hover to see operator/municipality/power.")


    # ===== Time series (LOCAL filters) =====
    st.subheader("How is deployment evolving?")
    st.write("A time trend shows whether deployment is accelerating, stable, or slowing, crucial for policy and investment pacing.")

    with st.expander("Time series filters (local)"):
        freq = st.selectbox("Frequency", ["Y (yearly)", "Q (quarterly)", "M (monthly)"], index=0)
        freq_map = {"Y (yearly)": "Y", "Q (quarterly)": "Q", "M (monthly)": "M"}
        freq_code = freq_map[freq]
        ops = sorted(df["nom_operateur"].dropna().unique()) if "nom_operateur" in df.columns else []
        ops_sel = st.multiselect("Operators (local)", ops, max_selections=10)
        if "annee_mise_en_service" in df.columns and df["annee_mise_en_service"].notna().any():
            ymin, ymax = int(df["annee_mise_en_service"].min()), int(df["annee_mise_en_service"].max())
            ysel = st.slider("Year range (local)", ymin, ymax, (ymin, ymax))
        else:
            ysel = None

    df_ts = df.copy()
    if ops_sel and "nom_operateur" in df_ts.columns:
        df_ts = df_ts[df_ts["nom_operateur"].isin(ops_sel)]
    if ysel and "annee_mise_en_service" in df_ts.columns:
        df_ts = df_ts[df_ts["annee_mise_en_service"].between(ysel[0], ysel[1])]

    st.plotly_chart(line_installations_over_time(df_ts, freq=freq_code), use_container_width=True)

    st.markdown(
        """
        **What we can observe:**
        - Deployment remained almost flat until around 2015, reflecting the early stage of EV adoption.  
        - From 2018 to 2023, installations grew exponentially, marking the rise of national strategies and private investment.  
        - The sharp drop after 2024 likely reflects data latency some recent points aren’t yet reported in open datasets.  
        - Overall, the trend tells a story of rapid acceleration, confirming that EV charging infrastructure is now a national priority.

        This timeline highlights how France moved from a few pilot projects to a large-scale rollout in just a few years — a turning point for electric mobility.
        """
    )

    st.caption("Takeaway: Acceleration suggests momentum; plateaus may point to permitting or supply bottlenecks.")

