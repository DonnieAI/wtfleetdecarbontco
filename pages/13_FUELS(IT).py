import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


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


URL = "https://prezzomediobenzina.it/?refresh_ce"

@st.cache_data(ttl=3600)
def load_fuel_prices_bs4():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(URL, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "prezzi_carburanti"})
    if table is None:
        raise ValueError("Table 'prezzi_carburanti' not found.")

    rows = []
    for tr in table.find_all("tr")[1:]:  # skip header
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(tds) == 3:
            rows.append(tds)

    df = pd.DataFrame(rows, columns=["Carburante", "Self", "Servito"])
    df["Self"] = pd.to_numeric(df["Self"], errors="coerce")
    df["Servito"] = pd.to_numeric(df["Servito"], errors="coerce")
    return df


st.title(f"🚚  UPDATED FUEL PRICES - IT")
st.markdown(f"""
### 📈 FUELS PRICE -real time 
""")
st.markdown("""
Source: https://prezzomediobenzina.it
""")

st.markdown("Fuel prices")
df_prices = load_fuel_prices_bs4()
st.dataframe(df_prices, use_container_width=True)


df = df_prices.copy()

# Treat 0 as missing
df["Self_clean"] = df["Self"].replace(0, np.nan)
df["Servito_clean"] = df["Servito"].replace(0, np.nan)

# Row-wise min and max ignoring zeros
df["min_val"] = df[["Self_clean", "Servito_clean"]].min(axis=1, skipna=True)
df["max_val"] = df[["Self_clean", "Servito_clean"]].max(axis=1, skipna=True)

# Remove rows where both are zero / missing
df = df.dropna(subset=["min_val", "max_val"]).copy()

# Sort decreasing
df = df.sort_values("max_val", ascending=False)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["min_val"],
    y=df["Carburante"],
    mode="markers",
    name="Min",
    marker=dict(size=10, symbol="circle"),
    hovertemplate="<b>%{y}</b><br>Min: %{x:.4f}<extra></extra>"
))

fig.add_trace(go.Scatter(
    x=df["max_val"],
    y=df["Carburante"],
    mode="markers",
    name="Max",
    marker=dict(size=10, symbol="diamond"),
    hovertemplate="<b>%{y}</b><br>Max: %{x:.4f}<extra></extra>"
))

fig.update_layout(
    title="Fuel prices: min and max",
    xaxis_title="Price",
    yaxis_title="Fuel",
    template="plotly_white",
    height=1500
)
fig.update_xaxes(
    dtick=0.2,
    tickformat=".1f",
    showgrid=True,
    gridwidth=0.5,
    color="white"
)
fig.update_yaxes(categoryorder="array", categoryarray=df["Carburante"])

st.plotly_chart(fig, use_container_width=True)