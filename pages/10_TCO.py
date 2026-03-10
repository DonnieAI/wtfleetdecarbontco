import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from datetime import datetime
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

#----------------------------------
#IMPORTING USERR DEFINED FUNCTIONS
import importlib
import supporting_functions as sf
importlib.reload(sf)

#----------------------------------
#----------------------------------

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


tco_data_files=["data/vehicle_data_full_data_set.csv",
                "data/fuel_consumption_manually.csv",
                "data/driver_wages.csv",
                "data/tolls_simplified_assumptions.csv"]

#✅------------------------DATA EXTRACTION-----------------------------------------------------
#df = pd.read_csv(tco_data_files[0], header=[0])
df=pd.read_csv("data/vehicle_main_class_parameter.csv")  #new approach
#df_consumptions_raw=pd.read_csv(tco_data_files[1], header=[0])
#df = pd.read_csv("data/vehicle_main_class_parameter.csv")

vehicles = sorted(df["Category"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().unique().tolist())

countries = {
    "ITALY": "ITALY",
    "GERMANY": "GERMANY",
    "AUSTRIA": "AUSTRIA"
}

st.title("🧮 TCO CALCULATOR")
st.caption("Source: WaveTransition")

st.divider()
st.subheader("🛣️ Main Vehicle Parameters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_country = st.selectbox(
        "Select country",
        list(countries.keys()),
        key="selected_country"
    )

with col2:
    selected_year = st.selectbox(
        "Select year",
        years,
        key="selected_year"
    )

with col3:
    selected_vehicle = st.selectbox(
        "Select Vehicle",
        vehicles,
        key="selected_vehicle"
    )

# ---- get default mileage from dataframe ----
mileage_col = "Annual_km"   # replace with your exact column name

row = df[
    (df["Category"] == selected_vehicle) &
    (df["Year"] == selected_year)
]

#default_mileage = 100000
if not row.empty and pd.notna(row.iloc[0][mileage_col]):
    default_mileage = int(row.iloc[0][mileage_col])

# ---- detect when vehicle/year changed ----
current_selector = (selected_vehicle, selected_year)

if "last_selector" not in st.session_state:
    st.session_state["last_selector"] = current_selector

if "YearlyMileageKm" not in st.session_state:
    st.session_state["YearlyMileageKm"] = default_mileage

if st.session_state["last_selector"] != current_selector:
    st.session_state["YearlyMileageKm"] = default_mileage
    st.session_state["last_selector"] = current_selector

with col4:
    YearlyMileageKm = st.number_input(
        "Yearly mileage [km]",
        min_value=5000,
        max_value=1000000,
        step=1000,
        key="YearlyMileageKm"
    )

#YearlyMileageKm=156000
filtered_df = df[(df["Category"] == selected_vehicle) & (df["Year"] == selected_year)]
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

#---------------TCO TABLE STRUCTURE CREATED----------------
df_tco_master = sf.tco_starting_template_builder(
            df_vehicle=df,
            country=selected_country,
            category=selected_vehicle,
            year=selected_year,
            YearlyMileageKm=YearlyMileageKm
    )
#----------------------------------------------------------------




#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️ General Parameters")
col1, col2, col3,col4,col5 = st.columns(5)
with col1:
    #st.subheader("Time [years]")
    VehicleLifeY = st.slider(
        "Time [years]",
        min_value=1,
        max_value=20,
        value=7,
        step=1,
        key="VehicleLifeY"
    )
    
with col2:   
    #st.subheader("WACC [%]")
    WACC = st.slider(
        "WACC [%]",
        min_value=1.0,
        max_value=20.0,
        value=7.0,
        step=0.5,
        key="WACC"
    )
    
with col3:   
    #st.subheader("TOLLS EURO 0-VI [EUR/100 km]")
    tolls_tarif_euro = st.slider(
        "TOLLS EURO 0-VI",
        min_value=0.0,
        max_value=100.0,
        value=32.5,
        step=0.5,
        key="tolls_tarif_euro"
    )

with col4:   
    #st.subheader("TOLLS  ZEV [EUR/100 km]")
    tolls_tarif_zev = st.slider(
        "TOLLS  ZEV",
        min_value=0.0,
        max_value=50.0,
        value=0.0,
        step=0.5,
        key="tolls_tarif_zev"
    )


df_tco_master["VehicleLifeY"]=VehicleLifeY


#-1️⃣-----------------calculate & merge total_capex
#df_capex = tco_capex_vehicle_calculator(df, selected_vehicle, selected_year)
data_all_df=pd.read_csv("data/capex_generated.data")
df_capex=sf.capex_calculator(data_all_df,selected_vehicle,selected_year )
df_tco_master = df_tco_master.merge(
            df_capex[["Category", "Technology", "Year", "TotalCapexEur"]],
            on=["Category", "Technology", "Year"],
            how="left",
            #suffixes=("", "_new")
)
# Replace the empty column with the computed one
#df_tco_master["TotalCapexEur"] = (
 #   pd.to_numeric(df_tco_master["capex_total_new"], errors="coerce")
  #  .round(0)
   # .astype("Int64")   # nullable integer (safe)
#)

#-1️⃣-----------------calculate & merge residual value
df_tco_master=sf.residual_value_calculator(1,0.23,df_tco_master,VehicleLifeY)
#df_tco_master.drop(columns=["capex_total_new"], inplace=True)
#----------------------------------------------------------------


#1️⃣-----------------calculate insurance cost based on residual value
df_tco_master=sf.insurance_calculator(df_tco_master,0.05)



#1️⃣-----------------calculate maintenance cost
df_maintenance = pd.read_csv("data/VehicleMaintenanceCost.csv")   #EUR/km
df_maintenance = df_maintenance[
    (df_maintenance["Category"] == selected_vehicle) &
    (df_maintenance["Year"] == selected_year)
    ]

df_tco_master=sf.maintenance_calculator(df_tco_master,df_maintenance)


#df_tco_master = df_tco_master.merge(
 #           df_maintenance[["Category", "Technology", "Year" ,"MaintenanceCostEurKm"]],
  #          on=["Category", "Technology", "Year"],
   #         how="left",
#)


#-1️⃣-----------------calculate & merge consumption
#-------------------------------
#df_consumptions=tco_fuel_consumption_manually_calculator(df,df_consumptions_raw,selected_vehicle, selected_year)
df_consumptions = pd.read_csv("data/FuelConsumptionManually.csv")
df_consumptions = df_consumptions[
    (df_consumptions["Category"] == selected_vehicle) &
    (df_consumptions["Year"] == selected_year)
]

df_tco_master = df_tco_master.merge(
            df_consumptions[["Category", "Technology", "Year" ,"FuelConsumption"]],
            on=["Category", "Technology", "Year"],
            how="left",
)



#-------------------------------
#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.subheader("🛣️ Prices")

col1, col2, col3, col4,col5 = st.columns(5)

with col1:
    #st.subheader("Diesel Price [EUR/l]")
    diesel_price = st.slider(
        "Diesel Price (EUR/l)",
        min_value=1.0,
        max_value=4.0,
        value=1.5,
        step=0.1,
        key="diesel_price"
    )

with col2:
    #st.subheader("LNG Price [EUR/kg]")
    lng_price = st.slider(
        "LNG Price (EUR/kg)",
        min_value=1.0,
        max_value=4.0,
        value=1.5,
        step=0.1,
        key="lng_price"
    )

with col3:
    #st.subheader("Electricity Price [EUR/kWh]")
    electricity_price = st.slider(
        "Electricity Price (EUR/kWh)",
        min_value=0.1,
        max_value=1.5,
        value=0.7,
        step=0.01,
        key="electricity_price"
    )

with col4:
    #st.subheader("H₂ Price [EUR/kg]")
    h2_price = st.slider(
        "H₂ Price (EUR/kg)",
        min_value=2.0,
        max_value=25.0,
        value=14.0,
        step=0.5,
        key="h2_price"
    )
    
with col5:
    #st.subheader("H₂ Price [EUR/kg]")
    ETS_CO2_Price = st.slider(
        "CO2 ETS Price (EUR/tCO2)",
        min_value=0.0,
        max_value=250.0,
        value=45.0,
        step=5.0,
        key="CO2price"
    )



#2️⃣FUEL COSTS------------------------------
df_fuel_cost = sf.tco_yearly_fuel_cost_calculator(
                df_consumptions,
                diesel_price,
                lng_price,
                electricity_price,
                h2_price,
                YearlyMileageKm
        )


df_tco_master = df_tco_master.merge(
            df_fuel_cost[["Category", "Technology", "AnnualFuelCostEur"]],
            on=["Category", "Technology" ],
            how="left",
            #suffixes=("", "_new")
        )
# Replace the empty column with the computed one
#df_tco_master["AnnualFuelCostEur"] = df_tco_master["annual_fuel_cost_new"]
# Drop helper column
#df_tco_master.drop(columns=["annual_fuel_cost_new"], inplace=True)
#----------------------------------------------------------------

#3️⃣TOLL-------------------------------

toll_map = {
        "ICE-D": tolls_tarif_euro,
        "ICE-NG": tolls_tarif_euro,
        "BET": tolls_tarif_zev,
        "FCET": tolls_tarif_zev
}
df_tco_master["AnnualTollCostEur"] = df_tco_master["Technology"].map(toll_map)*df_tco_master["YearlyMileageKm"]/100


#4️⃣WAGES-----------------------------
df_wages = pd.read_csv(tco_data_files[2], header=[0])   #Unitary_Wage_km
df_tco_master = sf.driver_wages_calculator(df_tco_master, df_wages)

#4️⃣CO2 ETS IMPACT-----------------------------
#ONLY FOR DIESEL
df_tco_master["ETSCO2CostEur"] = np.where(
    df_tco_master["Technology"].eq("ICE-D"),
    df_tco_master["FuelConsumption"] * 2.68 /100 * ETS_CO2_Price*df_tco_master["YearlyMileageKm"]/1000,  
    np.nan
)
df_tco_master["ETSCO2CostEur"] = df_tco_master["ETSCO2CostEur"].round().astype("Int64")

#-------------------------
#the core of the calculation
#----------------------------------------------
df_tco_master = df_tco_master.drop(columns=["Unitary_Wage_km","ResidualValuePct","FuelConsumption","MaintenanceCostEurKm"])
df_tco=sf.tco_calculator(WACC,VehicleLifeY,df_tco_master)
#----------------------------------------------
df_tco.to_csv("tco.csv")


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
    go.Bar(
        y=df_tco["Technology"],
        x=df_tco["TCO_MAINT_EUR_per_km"],
        name="Maintenance",
        orientation="h",
        marker=dict(color=palette_blue[4]),
    )
)

fig.add_trace(
    go.Bar(
        y=df_tco["Technology"],
        x=df_tco["TCO_ETS_CO2_per_km"],
        name="ETS CO2",
        orientation="h",
        marker=dict(color=palette_other[2]),
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
    template="plotly_white",
    legend_title="Component",
    margin=dict(l=40, r=40, t=60, b=40),
    xaxis=dict(
        title="EUR / km",
        range=[0, 2.2],      # fixed x-axis
        dtick=0.1,
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1,
        zeroline=False
    ),
    yaxis=dict(
        title="Technology"
    )
)

# vertical line at x = 1
fig.add_vline(
    x=1,
    line_width=2,
    line_dash="dash",
    line_color="black"
)

st.plotly_chart(fig, use_container_width=True)

#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------
st.dataframe(
    df_tco_master,
    use_container_width=True,
    hide_index=True
)