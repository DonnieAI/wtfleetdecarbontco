import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()


SEGMENT="LDT"

palette_blue = [
    "#A7D5F2",  # light blue
    "#94CCE8",
    "#81C3DD",
    "#6FBBD3",
    "#5DB2C8",
    "#A9DEF9",  # baby blue
]

palette_green = [
    "#6DC0B8",  # pastel teal
    "#7DCFA8",
    "#8DDC99",
    "#9CE98A",
    "#ABF67B",
    "#C9F9D3",  # mint green
    "#C4E17F",  # lime green
]

palette_other = [
    "#FFD7BA",  # pastel orange
    "#FFE29A",  # pastel yellow
    "#FFB6C1",  # pastel pink
    "#D7BDE2",  # pastel purple
    "#F6C6EA",  # light rose
    "#F7D794",  # peach
    "#E4C1F9",  # lavender
]
color_map={
    "DIESEL":palette_other[1],
    "PETROL":palette_other[2],
    "HYBRID":palette_blue[4],
    "EV":palette_green[3],
    "OTHERS":palette_green[1]
}


#✅------------------------DATA EXTRACTION-----------------------------------------------------

df = pd.read_csv("data/fuel_consumption_manually.csv", header=[0])

categories = sorted(df["Category"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().unique().tolist())


st.title(f"🚚  ZERO EMISSIONS VEHICLES - CONSUMPTIONS")
st.markdown(f"""
### 📈 CONSUMPTIONS  
""")
st.markdown("""
Source: ACEA — 2025 data
""")

selected_category = st.selectbox(
    "Select category",
    categories,
    index=categories.index("HDT") if "HDT" in categories else 0,
    key="category_selector"
)

selected_year = st.selectbox(
    "Select year",
    years,
    index=years.index(2025) if 2025 in years else 0,
    key="year_selector"
)

# Filter
df_filtered = df[(df["Category"] == selected_category) & (df["Year"] == selected_year)].copy()

# Optional: order by value
df_filtered = df_filtered.sort_values("Value_LDE", ascending=True)

# Plot (horizontal bar)
fig = go.Figure(
    go.Bar(
        y=df_filtered["Technology"],
        x=df_filtered["Value_LDE"],
        orientation="h",
        name="Value_LDE",
        marker=dict(color=palette_blue[0]),  # or any color you like
        hovertemplate="Technology: %{y}<br>Value_LDE: %{x:,.2f}<extra></extra>"
    )
)

fig.update_layout(
    title=f"Value_LDE by Technology — {selected_category} {selected_year}",
    xaxis_title="Value_LDE [litres/100km]",
    yaxis_title="Technology",
    template="plotly_white",
    height=450,
    margin=dict(l=40, r=20, t=60, b=40),
    xaxis=dict(showgrid=True)  # add grid if you want
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 Data table (filtered)")

# Optional: reorder columns (keep all)
cols = ["Category", "Technology", "Year", "Unit", "Value", "Conversion", "Value_LDE"]
df_table = df_filtered[cols].copy()

# Optional: formatting
df_table["Value"] = df_table["Value"].round(3)
df_table["Conversion"] = df_table["Conversion"].round(6)
df_table["Value_LDE"] = df_table["Value_LDE"].round(3)

st.dataframe(
    df_table,
    use_container_width=True,
    hide_index=True
)
