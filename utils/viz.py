import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

# -----------------------------
# Helpers: defensive casting
# -----------------------------
def _ensure_datetime(df: pd.DataFrame, col: str) -> pd.Series:
    """
    WHY: Many open datasets store dates as strings.
    Converting with errors='coerce' guarantees we get real datetimes for time series,
    and silently drops invalid ones instead of crashing the app.
    """
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found.")
    return pd.to_datetime(df[col], errors="coerce")

def _ensure_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    """
    WHY: Plotting, bins, and map sizing require numeric values.
    errors='coerce' turns bad values into NaN so visuals remain stable.
    """
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found.")
    return pd.to_numeric(df[col], errors="coerce")

def _order_power_categories(series: pd.Series) -> pd.Series:
    """
    WHY: Enforce a human-understandable order for power categories
    so bars appear Normal→Fast→Very fast→Ultra-fast instead of alphabetical.
    """
    cat_order = [
        "Normal (<22kW)",
        "Fast (22–50kW)",
        "Very fast (50–150kW)",
        "Ultra-fast (>150kW)",
    ]
    return series.astype(pd.CategoricalDtype(categories=cat_order, ordered=True))

# -----------------------------
# Map (pydeck)
# -----------------------------
def map_irve_points(
    df: pd.DataFrame,
    lat_col: str = "consolidated_latitude",
    lon_col: str = "consolidated_longitude",
    puissance_col: str = "puissance_nominale",
    tooltip_cols: list | None = None,
    initial_view: dict | None = None,
) -> pdk.Deck:
    """
    WHY: The map answers “where are the points?” — core to accessibility & equity.
    - Robust casting avoids failures due to bad lat/lon.
    - Point size scales (softly) with power to hint at capacity without clutter.
    - Green markers echo EV/eco semantics and improve contrast on light basemaps.
    """
    if tooltip_cols is None:
        tooltip_cols = []

    df = df.copy()
    df["__lat"] = _ensure_numeric(df, lat_col)
    df["__lon"] = _ensure_numeric(df, lon_col)
    # Size cap avoids giant circles from extreme values while still encoding power
    df["__size"] = (
        np.clip(_ensure_numeric(df, puissance_col).fillna(7), 5, 40)
        if puissance_col in df.columns else 8
    )

    # Center on France by default; sensible starting zoom for a national view
    if initial_view is None:
        initial_view = dict(latitude=46.6, longitude=2.5, zoom=5.3, pitch=0, bearing=0)

    # Build compact, informative tooltips (only existing columns)
    tooltip_text = "<b>Lat:</b> {__lat}<br/><b>Lon:</b> {__lon}"
    for c in tooltip_cols:
        if c in df.columns:
            tooltip_text += f"<br/><b>{c}:</b> {{{c}}}"
    if puissance_col in df.columns:
        tooltip_text += f"<br/><b>Power (kW):</b> {{{puissance_col}}}"

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df.dropna(subset=["__lat", "__lon"]),  # drop rows that can’t be mapped
        get_position=["__lon", "__lat"],
        get_radius="__size * 200",                 # WHY: perceptible sizing without covering the map
        radius_min_pixels=2,
        radius_max_pixels=50,
        get_fill_color=[0, 180, 0, 160],           # WHY: eco green, semi-transparent for overlap
        pickable=True,                             # WHY: enables hover tooltips
        filled=True,
        opacity=0.5,                               # WHY: see clusters without hiding base map
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(**initial_view),
        tooltip={"html": tooltip_text, "style": {"fontSize": "12px"}},
        map_style="light",
    )

# -----------------------------
# Time series
# -----------------------------
def line_installations_over_time(
    df: pd.DataFrame,
    date_col: str = "date_mise_en_service",
    freq: str = "Y",
    title: str = "New charging points put into service",
) -> go.Figure:
    """
    WHY: Tracking new installations reveals acceleration vs. slowdown — essential for policy/investment pacing.
    - Period grouping (Y/Q/M) provides flexible storytelling (annual strategy vs. seasonal rollouts).
    """
    s = _ensure_datetime(df, date_col)
    ts = s.dropna().dt.to_period(freq).value_counts().sort_index()
    ts = ts.rename_axis("period").reset_index(name="count")
    ts["period"] = ts["period"].astype(str)

    fig = px.line(ts, x="period", y="count", markers=True, title=title)
    fig.update_traces(hovertemplate="Period=%{x}<br>Points=%{y}")
    fig.update_layout(
        xaxis_title="Period", yaxis_title="Number of points",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    return fig

# -----------------------------
# Top operators (bar)
# -----------------------------
def bar_top_entities(
    df: pd.DataFrame,
    entity_col: str = "nom_operateur",
    top_n: int = 15,
    title: str | None = None,
) -> go.Figure:
    """
    WHY: Market structure matters — concentration vs. fragmentation impacts roaming, pricing, and resilience.
    - Horizontal bars + sorting highlight relative magnitudes with readable labels.
    """
    if entity_col not in df.columns:
        raise KeyError(f"Column '{entity_col}' not found.")
    vc = df[entity_col].fillna("Unknown").value_counts().head(top_n).sort_values(ascending=True)
    data = vc.reset_index(); data.columns = [entity_col, "count"]

    if title is None:
        title = f"Top {top_n} — {entity_col.replace('_', ' ').title()}"

    fig = px.bar(data, x="count", y=entity_col, orientation="h", title=title, text="count")
    fig.update_layout(
        xaxis_title="Number of points", yaxis_title="",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig

# -----------------------------
# Power category mix (bar)
# -----------------------------
def bar_power_categories(
    df: pd.DataFrame,
    cat_col: str = "categorie_puissance",
    title: str = "Charging power categories",
) -> go.Figure:
    """
    WHY: Power levels define user experience (minutes vs. hours).
    Showing the mix clarifies whether the network favors destination charging or high-speed corridors.
    """
    if cat_col not in df.columns:
        raise KeyError(f"Column '{cat_col}' not found.")
    ser = _order_power_categories(df[cat_col].astype(str))
    counts = pd.Series(ser).value_counts().reindex(ser.cat.categories, fill_value=0)
    data = counts.reset_index(); data.columns = [cat_col, "count"]

    fig = px.bar(data, x=cat_col, y="count", text="count", title=title)
    fig.update_layout(
        xaxis_title="Category", yaxis_title="Number of points",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig

# -----------------------------
# Power distribution (histogram)
# -----------------------------
def hist_power_distribution(
    df: pd.DataFrame,
    power_col: str = "puissance_nominale",
    title: str = "Power distribution (kW)",
    nbins: int = 40,
) -> go.Figure:
    """
    WHY: The distribution reveals typical charging speeds and whether there’s a high-kW tail for corridors.
    - 99th percentile cap keeps a few extreme values from flattening the entire histogram.
    """
    s = _ensure_numeric(df, power_col).dropna()
    cap = np.nanpercentile(s, 99)
    s = s.clip(upper=cap)

    fig = px.histogram(s, nbins=nbins, title=title)
    fig.update_layout(
        xaxis_title="Power (kW)", yaxis_title="Number of points",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    return fig

# -----------------------------
# Missingness overview (bar)
# -----------------------------
def bar_missingness(
    df: pd.DataFrame,
    top_n: int = 20,
    title: str = "Top columns by missing rate",
) -> go.Figure:
    """
    WHY: Transparency about data quality builds trust.
    Surfacing the most incomplete fields guides cleaning priorities and prevents misinterpretation.
    """
    miss = df.isnull().mean().sort_values(ascending=False).head(top_n) * 100
    data = miss.sort_values(ascending=True).reset_index()
    data.columns = ["column", "pct_missing"]

    fig = px.bar(
        data, x="pct_missing", y="column", orientation="h", title=title,
        text=data["pct_missing"].round(1).astype(str) + " %"
    )
    fig.update_layout(
        xaxis_title="% missing", yaxis_title="",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig
