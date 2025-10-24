README — Data Storytelling Dashboard (IRVE France)
- Project Overview

This project is a data storytelling dashboard built with Streamlit.
It explores France’s public EV charging infrastructure (IRVE) using open data from data.europa.eu.

The goal is simple:

Help planners, operators, and citizens see whether the charging network is equitable, reliable, and fast enough for real-world travel.

It transforms messy open data into a transparent, interactive story that blends analytics and narrative.

- Technical Requirements

Python ≥ 3.10

Streamlit ≥ 1.33

Libraries:

pandas
numpy
plotly
pydeck
streamlit


Install dependencies with:
pip install -r requirements.txt

How to Run the App:
1. Open a terminal in the project directory and run:
python -m streamlit run app.py

2. Streamlit will open automatically in your browser

Project Structure
app.py
 ├─ sections/
 │   ├─ intro.py          # Introduction and context
 │   ├─ overview.py       # KPIs, time trends, geographic overview
 │   ├─ deep_dives.py     # Operators, power levels, distributions
 │   └─ conclusions.py    # Insights, quality checks, next steps
 │
 ├─ utils/
 │   ├─ io.py             # Data loading (cached, automatic)
 │   ├─ prep.py           # Cleaning and normalization
 │   └─ viz.py            # Chart and map helpers (consistent visuals)
 │
 ├─ data/                 # Optional processed or cached datasets


Data Cleaning

Before visualization, the raw IRVE dataset is cleaned to make it analysis-ready.
Steps include:

Normalizing column names

Converting dates to datetime format

Removing invalid coordinates

Categorizing charging power levels

Deduplicating charge points

Keeping only relevant, clean fields

This ensures accuracy and transparency before storytelling begins.

Dashboard Structure (Story Flow) :
Section	Purpose
1️ Data Cleaning & Intro	Explains the dataset, its structure, and why cleaning is crucial for trust.
2️ Overview	Shows deployment trends, KPIs, and a national map. Answers “Where and how fast?”.
3️ Deep Dives	Examines who operates the network and what power levels are available. Answers “Who runs it and how powerful?”.
4️ Conclusions	Connects insights to policy and planning. Evaluates equity, reliability, and readiness for travel.

