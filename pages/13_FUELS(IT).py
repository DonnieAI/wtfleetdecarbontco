import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

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


st.title("Fuel prices")
df_prices = load_fuel_prices_bs4()
st.dataframe(df_prices, use_container_width=True)