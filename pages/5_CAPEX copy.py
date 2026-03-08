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
df = pd.read_csv("data/vehicle_data_full_data_set.csv", header=[0])
        # Store data
#print(df)
data = df.to_dict("records")
# Create unique option lists
categories = sorted(df["Category"].dropna().unique().tolist())
years = sorted(df["Year"].dropna().unique().tolist())
category_options = [{"label": cat, "value": cat} for cat in categories]
year_options = [{"label": str(yr), "value": yr} for yr in sorted(years)]


#ICE-D
data_ICE_D_df=pd.read_csv("data/vehicle_data_full_data_set_ICE-D.csv", header=[0])
data_ICE_D_df["capex_energy"]=data_ICE_D_df["FuelTankCost"]*data_ICE_D_df["TankSize"]
data_ICE_D_df["capex_power"]=data_ICE_D_df["PowerTrainCost"]*data_ICE_D_df["PowerTrain"]
data_ICE_D_df["capex_fixed"]=data_ICE_D_df["RestOfTruckCostTotal"]

#ICE-NG
data_ICE_NG_df=pd.read_csv("data/vehicle_data_full_data_set_ICE-NG.csv", header=[0])
data_ICE_NG_df["capex_energy"]=data_ICE_NG_df["FuelTankCost"]*data_ICE_NG_df["TankSize"]

data_ICE_NG_df["capex_power"]=data_ICE_NG_df["PowerTrainCost"]*data_ICE_NG_df["PowerTrain"]
data_ICE_NG_df["capex_fixed"]=data_ICE_NG_df["RestOfTruckCostTotal"]


#FCET
data_FCET_df=pd.read_csv("data/vehicle_data_full_data_set_FCET.csv", header=[0])
data_FCET_df["capex_energy"]=data_FCET_df["BatteryCost"]*data_FCET_df["BatterySize"]+\
          data_FCET_df["H2TankCost"]*data_FCET_df["H2Tank"]
data_FCET_df["capex_power"]=data_FCET_df["FuelCellsCost"]*data_FCET_df["FuelCellsPower"]+\
          data_FCET_df["PowerTrainCost"]*data_FCET_df["PowerTrain"]
data_FCET_df["capex_fixed"]=data_FCET_df["RestOfTruckCostTotal"]

#BET
data_BET_df=pd.read_csv("data/vehicle_data_full_data_set_BET.csv", header=[0])
data_BET_df["capex_energy"]=data_BET_df["BatteryCost"]*data_BET_df["BatterySize"]
data_BET_df["capex_power"]=data_BET_df["PowerTrainCost"]*data_BET_df["PowerTrain"]
data_BET_df["capex_fixed"]=data_BET_df["RestOfTruckCostTotal"]



data_all_df = pd.concat([data_ICE_D_df, data_ICE_NG_df,data_FCET_df,data_BET_df], ignore_index=True)

def capex_vehicle_calculator(df_in: pd.DataFrame,vehicle:str, year:int) -> pd.DataFrame:
    
    """
    The phases space is made by Category, Year and technology
    """
    df = df_in.copy()  # avoid mutating the caller's DataFrame
    df = df[(df["Category"] == vehicle) & (df["Year"] == year)]
    # Categorical for the first two columns
    df[["Category", "Technology"]] = df[["Category", "Technology"]].astype("category")
    # Convert all other columns to float (coerce in case there are stray strings)
    numeric_cols = df.columns.difference(["Category", "Technology"])
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    # Create capex columns
    
    df = (
        df
       # .assign(
        #    capex_energy = df["Energy_Storage_Cost"] * df["Energy"],
        #    capex_power  = df["Powertrain_Cost"]    * df["Power"],
        #    capex_fixed  = df["Rest_of_Truck_Cost"] + df["Other_cost"],
        #)
        .assign(
            capex_total = lambda d: d["capex_energy"] + d["capex_power"] + d["capex_fixed"]
        )
    )
    subset=["Category","Year","Technology","capex_energy","capex_power","capex_fixed","capex_total"]
    subset_df=df[subset]
    
    return subset_df

#-------------------------------
st.title(f"🚚  ZERO EMISSIONS VEHICLES - CAPEX")
st.markdown(f"""
### 📈 CAPEX  
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


df_filtered=capex_vehicle_calculator(data_all_df,selected_category,selected_year )

# Assume df_filtered already contains the filtered HDT 2025 data
df_plot = df_filtered.copy()
num_cols = df_plot.select_dtypes(include="number").columns
df_plot[num_cols] = df_plot[num_cols].round(0).astype(int)
# --- Capex Energy ---
fig = go.Figure()
fig.add_trace(
    go.Bar(
        y=df_plot["Technology"],
        x=df_plot["capex_energy"],
        name="Energy Storage",
        orientation="h",
        marker=dict(color=palette_green[2])
    )
)

# --- Capex Power ---
fig.add_trace(
    go.Bar(
        y=df_plot["Technology"],
        x=df_plot["capex_power"],
        name="Powertrain",
        orientation="h",
        marker=dict(color=palette_blue[2])
    )
)

# --- Capex Fixed ---
fig.add_trace(
    go.Bar(
        y=df_plot["Technology"],
        x=df_plot["capex_fixed"],
        name="Fixed Cost",
        orientation="h",
        marker=dict(color=palette_other[2])
    )
)

fig.update_layout(
    barmode="stack",
    title=f"CAPEX Breakdown — {selected_category} {selected_year}",
    xaxis_title="Cost (€)",
    yaxis_title="Technology",
    template="plotly_white",
    legend_title="Component",
    height=500
)
fig.update_layout(
    barmode="stack",
    template="plotly_white",
    xaxis=dict(
        showgrid=True,
        gridcolor="white",
        gridwidth=1
    )
)

fig.add_trace(
        go.Scatter(
            y=df_plot["Technology"],
            x=df_plot["capex_total"],
            mode="markers",
            name="capex",
            marker=dict(
                symbol="diamond",
                size=12,
                color="red",
                line=dict(width=3, color="white")
            ),
        )
    )


st.plotly_chart(fig, use_container_width=True)

#df_plot = df_plot.astype(int)

st.dataframe(
    df_plot,
    use_container_width=True,
    hide_index=True
)


