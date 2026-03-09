import streamlit as st
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()


#IMPORTING USERR DEFINED FUNCTIONS
import importlib
import supporting_functions as sf
importlib.reload(sf)

#-------------------------------------
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


coefficients = {
        "ICE-D": {"A": 0.0903, "B": -0.6404, "unit": "L/km", "lde": 1},
        "ICE-NG": {"A": 0.0694, "B": -0.4650, "unit": "kgNG/km", "lde": 0.72},
        "FCET": {"A": 0.01973, "B": -0.1233, "unit": "kgH2/km", "lde": 0.3},
        "BET": {"A": 0.3814, "B": -2.6735, "unit": "kWh/km", "lde": 10}
    }


#✅------------------------DATA EXTRACTION-----------------------------------------------------

df = pd.read_csv("data/FuelConsumptionManually.csv", header=[0])

categories = sorted(df["Category"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().unique().tolist())


st.title(f"🚚   CONSUMPTIONS")
st.markdown(f"""
### 📈 CONSUMPTIONS  
""")
st.markdown("""
Source: Wavetransition elaboration
""")


st.subheader("Gross Combination Weight - GCW [t]")
GCW = st.slider(
        "GCW [t]",
        min_value=10,
        max_value=50,
        value=40,
        step=1,
        key="GCW"
    )

#weight_kg = GCW * 1000   #must be in kg for the fucntion EC=a*ln(w)+b


df_consumption = sf.consumption_calculator(GCW,coefficients)



st.dataframe(
            df_consumption,
            use_container_width=True,
            hide_index=True
        )

technology_all=sorted(df["Technology"].unique())
color_map = {m: palette_other[i % len(palette_other)] for i, m in enumerate(technology_all)}

# Plot (horizontal bar)
fig = go.Figure(
    go.Bar(
        y=df_consumption["Technology"],
        x=df_consumption["Value_LDE_100km"],
        orientation="h",
        name="Value_LDE",
        marker=dict(
            color=[color_map[m] for m in df_consumption["Technology"]]
        ),
        hovertemplate="Technology: %{y}<br>Value_LDE: %{x:,.2f}<extra></extra>"
    )
)

fig.update_layout(
    title=f"Value_LDE by Technology ",
    xaxis_title="Value_LDE [litres/100km]",
    yaxis_title="Technology",
    template="plotly_white",
    height=450,
    margin=dict(l=40, r=20, t=60, b=40),
    xaxis=dict(showgrid=True)  # add grid if you want
)

st.plotly_chart(fig, use_container_width=True)




