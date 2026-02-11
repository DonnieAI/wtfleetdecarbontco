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

#✅------------------------DATA EXTRACTION----------------------------


VEHICLE_CLASS_MAP = {
    "LDT": {
        "AT": "2",                 # 2 axles
        "DE": "3.5-7.5t",          # light band
        "IT": "B",                 # 2 axles high vehicle (commercial van)
    },
    "MDT": {
        "AT": "3",                 # 3 axles
        "DE": "12-18t",            # medium weight band
        "IT": "3",                 # 3 axles
    },
    "HDT": {
        "AT": "4plus",             # 4+ axles
        "DE": ">18t",        # heavy + 5 axles
        "IT": "5",                 # 5 axles
    }
}


df_it=pd.read_csv("data/tolls_it.csv", header=[0])
terrain = sorted(df_it["terrain"].dropna().unique().tolist())


df_de=pd.read_csv("data/tolls_de.csv", header=[0])
axle_band_de = sorted(df_de["axle_band"].dropna().unique().tolist())

df_at=pd.read_csv("data/tolls_at.csv", header=[0])
axle_category_at = sorted(df_at["axle_category"].dropna().unique().tolist())


#-------------------------------
st.title(f"🚚  TOLLS")
st.markdown(f"""
### 📈 TOLLS
""")
st.markdown("""
Source: ACEA — 2025 data
""")



categories = ["LDT","MDT","HDT","BUSES"]
selected_category = st.selectbox(
    "Select category",
    categories,
    index=categories.index("HDT") if "HDT" in categories else 0,
    key="category_selector"
)

it_class = VEHICLE_CLASS_MAP[selected_category]["IT"]
de_class = VEHICLE_CLASS_MAP[selected_category]["DE"]
at_class = VEHICLE_CLASS_MAP[selected_category]["AT"]

EURO_CLASSES = [
    "EuroVI",
    "EuroV_EEV",
    "EuroIV",
    "EuroIII",
    "EuroII",
    "EuroI",
    "Euro0"
]

CO2_CLASSES=[1,2,3,4,5]

selected_euro_class = st.selectbox(
    "Select EURO CLASS",
    EURO_CLASSES,
    index=EURO_CLASSES.index("EuroVI") if "EuroVI" in EURO_CLASSES else 0,
    key="euro_classes_selector"
)

selected_co2_class = st.selectbox(
    "Select CO2 CLASS",
    CO2_CLASSES,
    index=CO2_CLASSES.index(4) if 4 in CO2_CLASSES else 0,
    key="co2_class_selector"
)

selected_terrain_it= st.selectbox(
    "Select terrain IT",
    terrain,
    index=terrain.index("flatland") if "flatland" in terrain else 0,
    key="terrain_selector"
)


selected_axle_de= st.selectbox(
    "Select axle DE",
    axle_band_de,
    index=axle_band_de.index("4 axles") if "4 axles" in axle_band_de else 0,
    key="axle_band_de_selector"
)



df_it_filtered = df_it[
    (df_it["vehicle_class"] == it_class) &
    (df_it["terrain"] == selected_terrain_it)
]

df_de_filtered = df_de[
    (df_de["weight_band"] == de_class) &
    (df_de["euro_class"] == selected_euro_class) &
    (df_de["axle_band"] ==selected_axle_de) &
    (df_de["co2_class"]== selected_co2_class)
]

df_at_filtered = df_at[
    (df_at["axle_category"] == at_class) &
    (df_at["emission_standard"] == selected_euro_class) &
    (df_at["co2_class"]== selected_co2_class)
   
]

df_it_filtered["unit_rate_eur_per_km"]
df_de_filtered["rate_cent_per_km"]
df_at_filtered["rate_total_eur_per_km"]

it_value = df_it_filtered["unit_rate_eur_per_km"].iloc[0] if not df_it_filtered.empty else 0

de_value = (
    df_de_filtered["rate_cent_per_km"].iloc[0] / 100
    if not df_de_filtered.empty else 0
)

at_value = df_at_filtered["rate_total_eur_per_km"].iloc[0] if not df_at_filtered.empty else 0

it_100 = it_value * 100
de_100 = de_value * 100
at_100 = at_value * 100


df_compare = pd.DataFrame({
    "Country": ["IT", "DE", "AT"],
    "Toll_EUR_100km": [it_100, de_100, at_100]
})

fig = go.Figure()

fig.add_trace(
    go.Bar(
        y=df_compare["Country"],
        x=df_compare["Toll_EUR_100km"],
        orientation="h",
        text=[f"{v:.2f} €" for v in df_compare["Toll_EUR_100km"]],
        textposition="outside",
        marker=dict(
            color=["#1f77b4", "#ff7f0e", "#2ca02c"]
        ),
        hovertemplate="Country: %{y}<br>Toll: %{x:.2f} €/100km<extra></extra>"
    )
)

fig.update_layout(
    title=f"Toll comparison — {selected_category}",
    xaxis_title="EUR / 100 km",
    yaxis_title="Country",
    template="plotly_white",
    height=450,
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig, use_container_width=True)