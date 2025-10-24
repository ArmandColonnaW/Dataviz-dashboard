import streamlit as st

def section_intro():
    """
    Story-driven introduction: why this dashboard exists, for whom, and how to read it.
    Keeps the function signature unchanged (no args).
    """

    # Title + provenance
    st.title("EV Charging Points in France (IRVE)")
    st.caption("Source: data.gouv.fr — Consolidated IRVE schema (Etalab) — Open License")

    # Why this dashboard
    st.markdown("### Why this dashboard?")
    st.write(
        "EV adoption only scales if people trust they can charge easily and quickly. "
        "This dashboard turns raw open data into an actionable story: where charging points are, "
        "how fast they charge, who operates them, and how deployments evolve."
    )
    st.success(
        "Goal in one sentence: **help planners, operators, and citizens see whether the network is equitable, "
        "reliable, and fast enough for real-world travel.**"
    )

    # Who is this for
    st.markdown("### Who is this for?")
    st.write(
        "- Local planners: spot coverage gaps and prioritize new sites.\n"
        "- Operators & retailers: benchmark presence and power mix.\n"
        "- Citizens & communities: understand availability and speed near them."
    )

    # Key questions answered (story arc)
    st.markdown("### What you’ll learn (story arc)")
    st.write(
        "1) **Overview**: How big is the network, where is it, and how fast is deployment?\n"
        "2) **Deep dives**: Who runs it and what power levels are offered?\n"
        "3) **Quality**: What’s missing, are there duplicates, and can we trust the picture?\n"
        "4) **Conclusions**: What to do next, based on the evidence."
    )

    # How to read (guided path)
    st.markdown("### How to read this dashboard")
    st.info(
        "Start with the map to grasp the geography, then the time trend for momentum. "
        "Use deep-dive charts to understand operators and power levels. "
        "Finally, check the data quality section to validate the story before taking action."
    )

    # Data notes / scope
    st.markdown("### Data notes & definitions")
    st.write(
        "- Each row ≈ a charging point (plug); several points can belong to one station.\n"
        "- Some administrative fields (pricing, INSEE) may be missing; we rely on GPS for mapping.\n"
        "- Power categories used throughout:\n"
        "  Normal (<22kW), Fast (22–50kW), Very fast (50–150kW), Ultra-fast (>150kW)."
    )
