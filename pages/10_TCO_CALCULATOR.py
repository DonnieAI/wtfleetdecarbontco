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
from utils import tco_capex_vehicle_calculator
from utils import tco_fuel_consumption_manually_calculator
from utils import yearly_fuel_cost
from utils import create_tco_template_from_data
from utils import apply_driver_wages

apply_style_and_logo()
#import importlib, utils
#importlib.reload(utils)

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

tco_data_files=["data/vehicle_data_full_data_set.csv",
                "data/fuel_consumption_manually.csv",
                "data/driver_wages.csv",
                "data/tolls_simplified_assumptions.csv"]

#✅------------------------DATA EXTRACTION-----------------------------------------------------

df = pd.read_csv(tco_data_files[0], header=[0])
df_consumptions_raw=pd.read_csv(tco_data_files[1], header=[0])

vehicles = sorted(df["Category"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().unique().tolist())
countries=sorted(["ITALY","GERMANY","AUSTRIA"])
countries = {
    "ITALY": "ITALY",
    "GERMANY": "GERMANY",
    "AUSTRIA": "AUSTRIA"
}


st.title(f"🧮  TCO CALCULATOR")
st.caption("Source: WaveTransition")

#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️ General Parameters")

col1, col2, col3,col4 = st.columns(4)
with col1:
    st.subheader("Country Selection")
    selected_country = st.selectbox(
        "Select country",
        list(countries.keys()),
        key="selected_country"
    )

with col2:
    st.subheader("Year Selection")
    selected_year = st.selectbox(
        "Select year",
        years,
        key="selected_year"
    )
    
with col3:
    st.subheader("Vehicle Selection")
    selected_vehicle = st.selectbox(
        "Select Vehicle",
        vehicles,
        key="selected_vehicle"
    )
with col4:
    st.subheader("Usage")
    yearly_mileage = st.number_input("Yearly mileage [km]", 
                              min_value=5000, 
                              max_value=1000000,
                              value=100000, 
                              step=1000,
                              key="yearly_mileage")

#---------------TCO TABLE STRUCTURE CREATED----------------
df_tco_master = create_tco_template_from_data(
    df_vehicle=df,
    country=selected_country,
    category=selected_vehicle,
    year=selected_year,
    annual_km_user=yearly_mileage
)
#----------------------------------------------------------------

#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️ General Parameters")

col1, col2, col3,col4 = st.columns(4)
with col1:
    st.subheader("Time [years]")
    T = st.slider(
        "Time [years]",
        min_value=1,
        max_value=20,
        value=7,
        step=1,
        key="T"
    )
    
with col2:   
    st.subheader("WACC [%]")
    WACC = st.slider(
        "WACC [%]",
        min_value=1.0,
        max_value=20.0,
        value=7.0,
        step=0.5,
        key="WACC"
    )
    
with col3:   
    st.subheader("TOLLS EURO 0-VI [EUR/100 km]")
    tolls_tarif_euro = st.slider(
        "TOLLS EURO 0-VI",
        min_value=0.0,
        max_value=100.0,
        value=32.5,
        step=0.5,
        key="tolls_tarif_euro"
    )

with col4:   
    st.subheader("TOLLS  ZEV [EUR/100 km]")
    tolls_tarif_zev = st.slider(
        "TOLLS  ZEV",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5,
        key="tolls_tarif_zev"
    )



#-1️⃣-----------------calculate & merge total_capex
df_capex = tco_capex_vehicle_calculator(df, selected_vehicle, selected_year)


df_tco_master = df_tco_master.merge(
    df_capex[["Category", "Technology", "Year", "capex_total"]],
    on=["Category", "Technology", "Year"],
    how="left",
    suffixes=("", "_new")
)
# Replace the empty column with the computed one
df_tco_master["capex_total"] = (
    pd.to_numeric(df_tco_master["capex_total_new"], errors="coerce")
    .round(0)
    .astype("Int64")   # nullable integer (safe)
)

df_tco_master.drop(columns=["capex_total_new"], inplace=True)
#----------------------------------------------------------------



#-------------------------------
df_consumptions=tco_fuel_consumption_manually_calculator(df,df_consumptions_raw,selected_vehicle, selected_year)
#-------------------------------
#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️ Fuel Price")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Diesel Price [EUR/l]")
    diesel_price = st.slider(
        "Diesel Price (EUR/l)",
        min_value=1.0,
        max_value=4.0,
        value=1.5,
        step=0.1,
        key="diesel_price"
    )

with col2:
    st.subheader("LNG Price [EUR/kg]")
    lng_price = st.slider(
        "LNG Price (EUR/kg)",
        min_value=1.0,
        max_value=4.0,
        value=1.5,
        step=0.1,
        key="lng_price"
    )

with col3:
    st.subheader("Electricity Price [EUR/kWh]")
    electricity_price = st.slider(
        "Electricity Price (EUR/kWh)",
        min_value=0.1,
        max_value=1.5,
        value=0.7,
        step=0.05,
        key="electricity_price"
    )

with col4:
    st.subheader("H₂ Price [EUR/kg]")
    h2_price = st.slider(
        "H₂ Price (EUR/kg)",
        min_value=2.0,
        max_value=25.0,
        value=14.0,
        step=0.5,
        key="h2_price"
    )
    

#2️⃣FUEL COSTS------------------------------
df_fuel_cost = yearly_fuel_cost(
        df_consumptions,
        diesel_price,
        lng_price,
        electricity_price,
        h2_price,
        yearly_mileage
)

df_fuel_cost = df_fuel_cost[[
    "Category",
    "Technology",
    "Unit",
    "Value",
    "Annual_consumption_user",
    "annual_fuel_cost"
]].copy()


df_tco_master = df_tco_master.merge(
    df_fuel_cost[["Category", "Technology",  "annual_fuel_cost"]],
    on=["Category", "Technology" ],
    how="left",
    suffixes=("", "_new")
)
# Replace the empty column with the computed one
df_tco_master["annual_fuel_cost"] = df_tco_master["annual_fuel_cost_new"]
# Drop helper column
df_tco_master.drop(columns=["annual_fuel_cost_new"], inplace=True)
#----------------------------------------------------------------

#3️⃣TOLL-------------------------------

toll_map = {
        "ICE-D": tolls_tarif_euro,
        "ICE-NG": tolls_tarif_euro,
        "BET": tolls_tarif_zev,
        "FCET": tolls_tarif_zev
}
df_tco_master["annual_toll_cost"] = df_tco_master["Technology"].map(toll_map)*df_tco_master["annual_km_user"]/100


#4️⃣WAGES-----------------------------
df_wages = pd.read_csv(tco_data_files[2], header=[0])   #Unitary_Wage_km
df_tco_master = apply_driver_wages(df_tco_master, df_wages)





def tco_calculator(i: float, T: int, df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simplified TCO (EUR/km) using:
      - capex_total (EUR)
      - annual_km_user (km/year)
      - annual_fuel_cost (EUR/year)

    i: discount rate (e.g., 0.05)
    T: lifetime (years)
    df: must contain capex_total, annual_km_user, annual_fuel_cost

    Output columns:
      TCO_CAPEX_EUR_per_km, TCO_FUEL_EUR_per_km, TCO_TOTAL_EUR_per_km
      + helper columns (CRF, discount_factor) optionally retained
    """
    i=i/100   # the WACC is passd as % here I need to rescale
    
    out = df.copy()

    # Basic validation / numeric coercion
    for c in ["capex_total", "annual_km_user", "annual_fuel_cost"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    # Avoid division by zero
    out["annual_km_user"] = out["annual_km_user"].replace(0, np.nan)
    
    # Capital Recovery Factor (CRF) and discounted sum factor
    CRF = (i * (1 + i) ** T) / (((1 + i) ** T) - 1) if i != 0 else (1 / T)
    discount_factor = sum(1 / ((1 + i) ** t) for t in range(1, T + 1)) if i != 0 else T

    # 1️⃣CAPEX component (annualized capex / annual km)
    out["TCO_CAPEX_EUR_per_km"] = (out["capex_total"] * CRF) / out["annual_km_user"]
    # 2️⃣FUEL component: discounted fuel over lifetime / (total km over lifetime)
    out["Total_discounted_fuel"] = out["annual_fuel_cost"] * discount_factor
    out["TCO_FUEL_EUR_per_km"] = out["Total_discounted_fuel"] / (out["annual_km_user"] * T)
    #3️⃣TOLL
    out["TCO_TOLL_EUR_per_km"]=out["annual_toll_cost"]/out["annual_km_user"]
    #3️⃣WAGES
    out["TCO_WAGES_EUR_per_km"]=out["annual_driver_cost"]/out["annual_km_user"]
    
    
    
    # Total
        
    out["TCO_TOTAL_EUR_per_km"] = out["TCO_CAPEX_EUR_per_km"] + out["TCO_FUEL_EUR_per_km"] +\
        out["TCO_TOLL_EUR_per_km"]+out["TCO_WAGES_EUR_per_km"]
    

    return out

df_tco=tco_calculator(WACC,T,df_tco_master)


#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️TCO COMPARISON")


fig = go.Figure()

    # CAPEX component
fig.add_trace(
        go.Bar(
            y=df_tco["Technology"],
            x=df_tco["TCO_CAPEX_EUR_per_km"],
            name="CAPEX",
            orientation="h",
            marker=dict(color=palette_blue[0]),
        )
    )

    # Fuel component
fig.add_trace(
        go.Bar(
            y=df_tco["Technology"],
            x=df_tco["TCO_FUEL_EUR_per_km"],
            name="Fuel",
            orientation="h",
            marker=dict(color=palette_green[0]),
        )
    )

fig.add_trace(
        go.Bar(
            y=df_tco["Technology"],
            x=df_tco["TCO_TOLL_EUR_per_km"],
            name="Toll",
            orientation="h",
            marker=dict(color=palette_other[0]),
        )
    )

fig.add_trace(
        go.Bar(
            y=df_tco["Technology"],
            x=df_tco["TCO_WAGES_EUR_per_km"],
            name="Wages",
            orientation="h",
            marker=dict(color=palette_blue[1]),
        )
    )


fig.add_trace(
        go.Scatter(
            y=df_tco["Technology"],
            x=df_tco["TCO_TOTAL_EUR_per_km"],
            mode="markers",
            name="Total TCO",
            marker=dict(
                symbol="diamond",
                size=12,
                color="red",
                line=dict(width=3, color="white")
            ),
        )
    )


fig.update_layout(
        barmode="stack",
        title="TCO Breakdown (EUR/km)",
        height=700,
        xaxis_title="EUR / km",
        yaxis_title="Technology",
        template="plotly_white",
        legend_title="Component",
        margin=dict(l=40, r=40, t=60, b=40),
    )

fig.update_layout(
    template="plotly_white",
    xaxis=dict(
        showgrid=True,
        gridcolor="white",
        gridwidth=1,
        dtick=0.1   # 👈 tick spacing = 0.2 EUR
    )
)

st.plotly_chart(fig, use_container_width=True)


st.dataframe(
    df_tco_master,
    use_container_width=True,
    hide_index=True
)