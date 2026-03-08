import streamlit as st
import pandas as pd
import numpy as np

def capex_calculator(df_in: pd.DataFrame,vehicle:str, year:int) -> pd.DataFrame:
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
          
            
    out["TCO_TOTAL_EUR_per_km"] = out["TCO_CAPEX_EUR_per_km"] + out["TCO_FUEL_EUR_per_km"] +\
        out["TCO_TOLL_EUR_per_km"]+out["TCO_WAGES_EUR_per_km"]
    

    return out