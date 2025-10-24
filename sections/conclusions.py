import streamlit as st
import pandas as pd
from utils.viz import bar_missingness

def _fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except Exception:
        return str(n)

def _power_category_series(df: pd.DataFrame) -> pd.Series | None:
    """Return a 'categorie_puissance' Series (create it if missing), otherwise None."""
    if "categorie_puissance" in df.columns:
        return df["categorie_puissance"].astype(str)
    if "puissance_nominale" in df.columns:
        s = pd.to_numeric(df["puissance_nominale"], errors="coerce")
        bins = [0, 22, 50, 150, 1000]
        labels = ["Normal (<22kW)", "Fast (22–50kW)", "Very fast (50–150kW)", "Ultra-fast (>150kW)"]
        return pd.cut(s, bins=bins, labels=labels, right=False).astype(str)
    return None

def _year_series(df: pd.DataFrame) -> pd.Series | None:
    if "date_mise_en_service" not in df.columns:
        return None
    s = pd.to_datetime(df["date_mise_en_service"], errors="coerce")
    if s.notna().any():
        return s.dt.year
    return None

def section_conclusion(df_raw: pd.DataFrame):
    st.header("3️ Conclusions — turn insights into action")

    # ---------- Build small dynamic facts ----------
    total_points = len(df_raw)
    cat_ser = _power_category_series(df_raw)
    ultra_share = None
    if cat_ser is not None and cat_ser.notna().any():
        ultra_share = (cat_ser == "Ultra-fast (>150kW)").mean() * 100

    # Growth signal (last 2 years vs. previous 2)
    yr = _year_series(df_raw)
    growth_msg = "Insufficient date coverage to estimate growth."
    if yr is not None and yr.notna().any():
        counts = yr.value_counts().sort_index()
        if len(counts.index) >= 4:
            last_year = int(counts.index.max())
            last2 = counts.get(last_year, 0) + counts.get(last_year - 1, 0)
            prev2 = counts.get(last_year - 2, 0) + counts.get(last_year - 3, 0)
            if prev2 > 0:
                ratio = last2 / prev2
                growth_msg = f"Installations in the last two years are {ratio:.1f}× the previous two."
            else:
                growth_msg = "Installations surged recently (little or no activity four years ago)."

    # Missingness snapshot
    avg_missing = df_raw.isna().mean().mean() * 100
    top_missing = (
        df_raw.isna().mean().sort_values(ascending=False).head(3) * 100
        if len(df_raw.columns) > 0
        else pd.Series(dtype=float)
    )
    top_missing_list = [f"{k} ({v:.0f}%)" for k, v in top_missing.items()]

    # Duplicates check
    keys = [k for k in ["id_pdc_itinerance", "id_pdc_local"] if k in df_raw.columns]
    dup_count = int(df_raw.duplicated(subset=keys).sum()) if keys else 0

    # ---------- Story banner ----------
    st.success(
        f"Story so far: the network counts {_fmt_int(total_points)} charging points in this dataset. "
        + (f"Ultra-fast (>150 kW) account for {ultra_share:.1f}% of points. " if ultra_share is not None else "")
        + growth_msg
    )

    # ---------- Storytelling paragraph responding to the main goal ----------
    st.markdown(
        """
        **How does this network perform for real-world travel?**  
        For planners, the data reveals where accessibility remains uneven rural “charging deserts” still exist, 
        but high-power hubs are expanding along national highways.  
        For operators, deployment speed and power diversity point to a maturing market that now balances volume 
        with quality.  
        And for citizens, the increasing share of ultra-fast points (≥150 kW) means electric travel is becoming 
        both faster and more reliable.  
        Together, these trends suggest a system moving toward **greater equity, reliability, and readiness for 
        everyday mobility.**
        """
    )

    # ---------- What to do next (actionable) ----------
    st.markdown("### What to do next")
    items = []
    if ultra_share is not None and ultra_share < 20:
        items.append("- **Boost ultra-fast along corridors** to enable reliable long-distance travel.")
    else:
        items.append("- **Sustain ultra-fast deployment** on strategic routes (motorways, ring roads).")
    items.append("- **Close charging deserts** highlighted by the map (rural/mountainous gaps).")
    if dup_count > 0:
        items.append(f"- **Deduplicate station records** ({_fmt_int(dup_count)} potential duplicates) to improve accuracy.")
    if avg_missing > 20:
        items.append(
            f"- **Enrich key attributes** (top missing: {', '.join(top_missing_list)}) to improve planning & monitoring."
        )
    st.write("\n".join(items))

    # ---------- Data quality & validation ----------
    st.markdown("### Data quality")
    with st.expander("Basic data checks"):
        if keys:
            st.write(f"Potential duplicates (using {', '.join(keys)}): {_fmt_int(dup_count)}")
        else:
            st.write("No unique keys available to detect duplicates.")
        msgs = []
        if "puissance_nominale" in df_raw.columns:
            neg = (pd.to_numeric(df_raw["puissance_nominale"], errors="coerce") < 0).sum()
            msgs.append(f"Negative power values: {_fmt_int(neg)}")
        if "consolidated_latitude" in df_raw.columns:
            bad_lat = ~df_raw["consolidated_latitude"].between(-90, 90)
            msgs.append(f"Latitude out of [-90,90]: {_fmt_int(bad_lat.sum())}")
        if "consolidated_longitude" in df_raw.columns:
            bad_lon = ~df_raw["consolidated_longitude"].between(-180, 180)
            msgs.append(f"Longitude out of [-180,180]: {_fmt_int(bad_lon.sum())}")
        st.write(" • " + "  \n • ".join(msgs) if msgs else "No simple anomalies detected.")

    st.subheader("Missing values (top columns)")
    st.plotly_chart(bar_missingness(df_raw), use_container_width=True)

    # ---------- Transparent limitations ----------
    st.markdown("### Limitations")
    lim = [
        "- Administrative fields can be incomplete; some stations might not have up-to-date attributes.",
        "- Installation dates can lag in open datasets, so very recent years may look artificially low.",
        "- Declared power may differ from effective charging speed (hardware, grid constraints, uptime).",
    ]
    st.write("\n".join(lim))

    # ---------- Extend the story ----------
    st.markdown("### How to extend this story")
    nxt = [
        "- Add **population/traffic context** (points per 10k residents, corridor density).",
        "- Track **uptime** and **pricing** if/when datasets become available.",
        "- Build a **what-if**: “How many >150 kW points do we need to meet 2030 corridor targets?”",
    ]
    st.write("\n".join(nxt))
