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
# 1. Read CSV with 2 header rows
df = pd.read_csv("data/ZEV_LowEmission_Models.csv", header=0).dropna()

#segment_list = sorted(df_ev["segment"].unique())
#df_ev["energy_kWh_clean"] = df_ev["energy_kWh"].fillna(0)

#max_energy = df_ev["energy_kWh_clean"].max()

#if max_energy > 0:
#    df_ev["marker_size"] = 10 + 30 * (df_ev["energy_kWh_clean"] / max_energy)
#else:
#    df_ev["marker_size"] = 10

# ------------------------------------------------------------
# Streamlit output
# ------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
st.title(f"🚚  ZERO EMISSIONS & LOW EMISSIONS VEHICLES")
st.markdown(f"""
### 📈 sdfdfdfs  
""")
st.markdown("""
Source: ACEA — 2025 data
""")


# 1) Segment selector
segments = sorted(df["SEGMENT"].unique())
selected_segment = st.selectbox(
    "Select segment",
    segments,
    index=segments.index("truck") if "truck" in segments else 0,
    key="segment_selector"
)

# 2) Filter data
df_f = df[df["SEGMENT"] == selected_segment].copy()

# 3) Build a stable color map (same manufacturer => same color)
palette = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

manufacturers_all = sorted(df["MANUFACTURER"].unique())
technology_all=sorted(df["TECHNOLOGY"].unique())
color_map = {m: palette[i % len(palette)] for i, m in enumerate(technology_all)}

# 4) Build go.Figure with one trace per manufacturer
fig_ev = go.Figure()

for m in sorted(df_f["TECHNOLOGY"].unique()):
    d = df_f[df_f["TECHNOLOGY"] == m]

    fig_ev.add_trace(
        go.Scatter(
            x=d["ENERGY"],
            y=d["RANGE"],
            mode="markers",
            name=m,
            marker=dict(
                    size=15,
                    color=color_map[m],
                    opacity=0.8,
                    line=dict(width=0.5, color="black")
                ),

        )
    )

# 5) Layout
fig_ev.update_layout(
    title=f"Range vs Max GVW — Segment: {selected_segment}",
    xaxis_title="Energy (kWh)",
    yaxis_title="Max Range (km)",
    template="plotly_white",
    legend_title="Manufacturer",
    margin=dict(l=40, r=20, t=60, b=40),
)

st.plotly_chart(fig_ev, use_container_width=True)

