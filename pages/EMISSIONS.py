import streamlit as st
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json

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



consumption_coefficients = {
    "ICE-D": {"consumption": 0.316, "consumption_MJ":11.31, "unit": "L/km", "lde": 1},  #36 MJ/l
    "ICE-NG": {"consumption": 0.27, "consumption_MJ":13.26,"unit": "kgNG/km", "lde": 0.72}, #49.1
    "FCET": {"consumption": 0.086, "consumption_MJ":10.32,"unit": "kgH2/km", "lde": 0.3},  #120
    "BET": {"consumption": 1.368,  "consumption_MJ":4.9248,"unit": "kWh/km", "lde": 10}  #3.6
}


#✅------------------------DATA EXTRACTION-----------------------------------------------

def load_config(json_path: str) -> dict:
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_technology_options(data: dict) -> list[str]:
    return list(data.get("technology_to_allowed_fuels", {}).keys())


def get_allowed_fuels(data: dict, technology: str) -> list[str]:
    return data.get("technology_to_allowed_fuels", {}).get(technology, [])


def get_fuel_display_map(data: dict, fuel_keys: list[str]) -> dict:
    fuels_data = data.get("fuels", {})
    return {
        fuel_key: fuels_data.get(fuel_key, {}).get("display_name", fuel_key)
        for fuel_key in fuel_keys
    }

def get_selected_fuel_data(data: dict, fuel_key: str) -> dict:
    return data.get("fuels", {}).get(fuel_key, {})

json_path = "data/fuels_pathway_red.json"
fuel_data = load_config(json_path)

technologies = get_technology_options(fuel_data)

st.title("🚚 EMISSIONS")
st.subheader("Selected combination")

col1, col2, col3 = st.columns(3)

with col1:
    selected_technology = st.selectbox(
        "Select technology",
        options=technologies,
        index=0,
    )

with col2:
    allowed_fuels = get_allowed_fuels(fuel_data, selected_technology)
    fuel_display_map = get_fuel_display_map(fuel_data, allowed_fuels)

    selected_fuel_key = st.selectbox(
        "Select fuel",
        options=allowed_fuels,
        format_func=lambda x: fuel_display_map[x],
        index=0,
    )

with col3:
    st.subheader("Usage")
    yearly_mileage = st.number_input("Yearly mileage [km]", 
                              min_value=5000, 
                              max_value=1000000,
                              value=100000, 
                              step=1000,
                              key="yearly_mileage")


st.subheader("Selected combination")
col1, col2 = st.columns(2)

with open(json_path) as f:
    data = json.load(f)
#FOSSIL DIESEL BENCHMARK

diesel_wtt_mj=data["fuels"]["fossil_diesel"]["wtt_gco2eq_per_mj_default"]
diesel_ttw_mj=data["fuels"]["fossil_diesel"]["combustion_gco2eq_per_mj"]
diesel_wtw_mj=diesel_wtt_mj+diesel_ttw_mj
# emissions based on km
#diesel_energy_mj_l = data["fuels"]["fossil_diesel"]["energy_content_by_volume_mj_per_l"] #MJ/l
#diesel_energy_mj_km = data["fuels"]["fossil_diesel"]["consumption_MJ"] #MJ/l
diesel_specific_consumption_MJ=consumption_coefficients.get("ICE-D",{}).get("consumption_MJ")  #MJ/km
#diesel_volume_energy=data["fuels"]["fossil_diesel"]["energy_content_by_volume_mj_per_l"]
diesel_lca_co2_emissions=diesel_specific_consumption_MJ*diesel_wtw_mj*1 #gCO2/km


# FUEL SELECTED
selected_fuel_data = get_selected_fuel_data(fuel_data, selected_fuel_key)
selected_fuel_wtt_mj = selected_fuel_data.get("wtt_gco2eq_per_mj_default")
selected_fuel_ttw_mj = selected_fuel_data.get("combustion_gco2eq_per_mj")
selected_fuel_wtw_mj=selected_fuel_wtt_mj+selected_fuel_ttw_mj
#selected_fuel_energy_mj_l=selected_fuel_data.get("energy_content_by_volume_mj_per_l")
# emissions based on km
specific_consumption=consumption_coefficients.get(selected_technology,{}).get("consumption_MJ")  #l/km
#diesel_volume_energy=data["fuels"]["fossil_diesel"]["energy_content_by_volume_mj_per_l"]
selected_fuel_lca_co2_emissions=specific_consumption*selected_fuel_wtw_mj*1 #gCO2/km


with col1:
    st.write("Fossil Diesel Benchamrk LCA emissions[gCO2/MJ]")
    st.write("WTT:", diesel_wtt_mj," | kgCO2/MJ")#gCO2/MJ
    st.write("TTW:", diesel_ttw_mj," | kgCO2/MJ")#gCO2/MJ
    st.write("WTW:", diesel_wtw_mj," | kgCO2/MJ")#gCO2/MJ 
    st.write("LCA diesel",int(diesel_lca_co2_emissions)," | kgCO2/km")
    
with col2:
    st.write("Selected fuel key:", selected_fuel_key)
    st.write("WTT:", selected_fuel_wtt_mj)#gCO2/MJ
    st.write("TTW:", selected_fuel_wtw_mj)#gCO2/MJ
    st.write("WTW:", selected_fuel_wtw_mj)#gCO2/MJ
    st.write("LCA selected fuel",int(selected_fuel_lca_co2_emissions)," | kgCO2/km")



label = selected_fuel_data.get("wtw_gco2eq_per_mj_default")

#Fuel use = 32.03 L/100 km
standard_diesel_consuption=32.03   #liter/100km
Energy_use=standard_diesel_consuption/100*36
#WTW_tCO2_y=Energy_use*diesel_wtw*yearly_mileage/1000000   #tCO2/y

#st.write("Diesel benchmanr [tCO2/y]:", int(WTW_tCO2_y))#gCO2/MJ


#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------



fig = go.Figure()

# diesel benchmark area
fig.add_shape(
    type="rect",
    x0=0,
    y0=0,
    x1=diesel_wtt_mj,
    y1=diesel_ttw_mj,
    fillcolor="lightgray",
    opacity=0.3,
    line=dict(width=0),
)

fig.add_annotation(
    x=diesel_wtt_mj,
    y=diesel_ttw_mj,
    text=f"Diesel benchmark<br>WTW={diesel_wtw_mj}",
    showarrow=False,
    xanchor="right",
)

# only plot point when both coordinates exist
if selected_fuel_wtt_mj is not None and selected_fuel_ttw_mj is not None:
    text_value = "n.a." if label is None else f"{label}"
    fig.add_trace(
        go.Scatter(
            x=[selected_fuel_wtt_mj],
            y=[selected_fuel_ttw_mj],
            mode="markers+text",
            text=[text_value],
            textposition="top center",
            marker=dict(size=14),
            name=fuel_display_map[selected_fuel_key],
        )
    )
else:
    st.warning(
        f"No complete default values available for {fuel_display_map[selected_fuel_key]}."
    )

fig.update_layout(
    title="Fuel Emissions Comparison vs Diesel Benchmark",
    xaxis_title="TTW emissions (gCO2eq/MJ)",
    yaxis_title="WTT emissions (gCO2eq/MJ)",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)