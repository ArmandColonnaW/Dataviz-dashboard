import streamlit as st
import pandas as pd
from utils.viz import bar_top_entities, bar_power_categories, hist_power_distribution
import plotly.express as px

def _fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except Exception:
        return str(n)

def section_deep_dives(df: pd.DataFrame):
    st.header("2️Deep dives — who runs it, and how fast can we charge?")

    st.info(
        "Why these dives? Operators affect reliability, pricing, and roaming. "
        "Power levels define user experience (minutes vs. hours). "
        "Understanding both helps target investments that actually move the needle."
    )

    # ===== Top operators (LOCAL filters) =====
    colA, colB = st.columns([1, 1])
    with colA:
        st.subheader("Who operates the most points?")
        st.caption("This ranking reveals market structure and potential single-points-of-failure.")
        with st.expander("Top chart filters (local)"):
            top_n = st.slider("Items to display", 5, 30, 15)
            min_kW = st.number_input("Minimum power (kW)", min_value=0.0, value=0.0, step=1.0, help="Local filter")

        df_top = df.copy()
        if "puissance_nominale" in df_top.columns:
            df_top = df_top[df_top["puissance_nominale"].fillna(0) >= float(min_kW)]

        st.plotly_chart(
            bar_top_entities(df_top, entity_col="nom_operateur", top_n=int(top_n)),
            use_container_width=True,
        )

        # --- Storytelling under the bar chart: dynamic observations ---
        if "nom_operateur" in df_top.columns and not df_top.empty:
            counts = df_top["nom_operateur"].fillna("Unknown").value_counts()
            total = int(counts.sum())
            top_op = counts.index[0]
            top_val = int(counts.iloc[0])
            share = 100 * top_val / total if total else 0
            top3 = counts.head(3)
            top3_list = [f"{name} ({_fmt_int(val)})" for name, val in top3.items()]
            st.markdown(
                f"""
**What we can observe:**
- {top_op} operates the largest number of points ({_fmt_int(top_val)}), about {share:.1f}% of the current view.
- The Top 3 operators are: {", ".join(top3_list)}.
- The long tail beyond the top few brands hints at a fragmented market, which can impact roaming and user experience.

Why it matters: concentration can create dependencies (outage risk, pricing power), whereas fragmentation can reduce interoperability.
"""
            )
        else:
            st.markdown(
                "**What we can observe:** No operator data available for the current filter selection."
            )

        st.caption("Why it matters: concentration risks, competitive dynamics, and roaming priorities.")

    # ===== Power categories (LOCAL filters) =====
    with colB:
        st.subheader("What power levels are offered?")
        st.caption("Power drives refuel time and shapes where people are comfortable switching to EVs.")
        with st.expander("Category chart filters (local)"):
            ops = sorted(df["nom_operateur"].dropna().unique()) if "nom_operateur" in df.columns else []
            ops_sel = st.multiselect("Operators to include", ops, help="Local filter for this chart", max_selections=15)

        df_cat = df.copy()
        if ops_sel and "nom_operateur" in df_cat.columns:
            df_cat = df_cat[df_cat["nom_operateur"].isin(ops_sel)]

        st.plotly_chart(bar_power_categories(df_cat), use_container_width=True)

        # --- Storytelling under the category chart: dynamic observations ---
        if "categorie_puissance" in df_cat.columns and not df_cat.empty:
            cat_counts = df_cat["categorie_puissance"].astype(str).value_counts()
            total_c = int(cat_counts.sum())
            dom_cat = cat_counts.idxmax()
            dom_val = int(cat_counts.max())
            dom_share = 100 * dom_val / total_c if total_c else 0
            # Build a short list of categories with shares
            cat_items = [f"{k} ({_fmt_int(v)} • {100*v/total_c:.1f}%)" for k, v in cat_counts.items()]
            st.markdown(
                f"""
**What we can observe:**
- {dom_cat} dominates the offer ({_fmt_int(dom_val)} points, {dom_share:.1f}% of the current view).
- Mix by category: {", ".join(cat_items)}.
- A higher share of Ultra-fast (>150kW) indicates better suitability for highways and long trips; a heavy Normal/22–50kW mix suggests focus on destination/urban charging.

Takeaway: aligning the power mix with travel patterns is key to real-world usability.
"""
            )
        else:
            st.markdown(
                "**🔎 What we can observe:** No power-category data available for the current filter selection."
            )

        st.caption("Takeaway: higher shares of ultra-fast suggest better suitability for highways and long trips.")

    # ===== Power distribution (LOCAL filters) =====
    st.subheader("How is power distributed?")
    st.caption("A distribution exposes outliers and shows whether the network clusters around common speeds.")
    with st.expander("Histogram filters (local)"):
        pmin = float(df["puissance_nominale"].min()) if "puissance_nominale" in df.columns else 0.0
        pmax = float(df["puissance_nominale"].max()) if "puissance_nominale" in df.columns else 350.0
        p_range = st.slider("Power range (kW, local)", pmin, pmax, (pmin, pmax))
        nbins = st.slider("Number of bins", 10, 100, 40)
        cap99 = st.checkbox("Cap at 99th percentile (reduces outliers)", value=True)

    df_hist = df.copy()
    if "puissance_nominale" in df_hist.columns:
        df_hist = df_hist[df_hist["puissance_nominale"].between(p_range[0], p_range[1], inclusive="both")]

    if not cap99:
        s = pd.to_numeric(df_hist["puissance_nominale"], errors="coerce").dropna()
        fig = px.histogram(s, nbins=int(nbins), title="Power distribution (kW) — no 99th cap")
        fig.update_layout(xaxis_title="Power (kW)", yaxis_title="Number of points",
                          margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(hist_power_distribution(df_hist, nbins=int(nbins)), use_container_width=True)

    # --- Storytelling under the histogram (dynamic, concise, decision-focused) ---
    if "puissance_nominale" in df_hist.columns and not df_hist.empty:
        import numpy as np

        s_clean = pd.to_numeric(df_hist["puissance_nominale"], errors="coerce").dropna()

        if not s_clean.empty:
            # Core stats
            p50 = s_clean.median()
            p75 = s_clean.quantile(0.75)
            p90 = s_clean.quantile(0.90)

            # Detect the two most populated power ranges (rough “peaks”)
            counts, bin_edges = np.histogram(s_clean, bins=20)
            top_idx = counts.argsort()[::-1][:2]  # indices of top 2 bins
            peaks = []
            for i in top_idx:
                lo = bin_edges[i]
                hi = bin_edges[i + 1]
                peaks.append(f"{lo:.0f}–{hi:.0f} kW")

            st.markdown(
                f"""
    **What we can observe:**
    - The median power is {p50:.1f} kW, with upper quartiles at {p75:.1f} kW (75th) and {p90:.1f} kW (90th).
    - The most common power ranges in this view are roughly {', '.join(peaks)}.
    - A concentration in lower bands suggests destination/urban charging; a visible tail into high-kW bands supports corridor / long-distance use.

    **Why it matters:** If most points concentrate below ~22–50 kW, typical sessions take longer (good for shopping/destination).
    More presence above 150 kW means fast turnarounds on highways and strategic routes.
    """
            )
        else:
            st.markdown("**What we can observe:** No valid power values for the current selection.")
    else:
        st.markdown("**What we can observe:** Histogram unavailable for the current selection.")
