import streamlit as st
import pandas as pd
import numpy as np



def tco_starting_template_builder(
    df_vehicle: pd.DataFrame,
    country: str,
    category: str,
    year: int,
    YearlyMileageKm: int
) -> pd.DataFrame:
    """
    Build the master TCO dataframe including Country and user annual mileage.
    One row per Technology for selected Category and Year.
    """

    df_filtered = df_vehicle[
        (df_vehicle["Category"] == category) &
        (df_vehicle["Year"] == year)
    ].copy()

    technologies = sorted(df_filtered["Technology"].dropna().unique().tolist())

    df_template = pd.DataFrame({
        "Country": [country] * len(technologies),
        "Category": [category] * len(technologies),
        "Technology": technologies,
        "Year": [year] * len(technologies),
        "YearlyMileageKm": [YearlyMileageKm] * len(technologies),
        
    })

    # Initialize calculation columns (filled later)
    """
    df_template["TotalCapexEur"] = pd.NA
    df_template["Unit"] = pd.NA
    df_template["consumption_per_100km"] = pd.NA
    df_template["annual_consumption_user"] = pd.NA
    df_template["AnnualFuelCostEur"] = pd.NA
    df_template["AnnualTollCostEur"]=pd.NA
    df_template["annual_wages_cost"]=pd.NA
    """
    return df_template



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
            TotalCapexEur = lambda d: d["capex_energy"] + d["capex_power"] + d["capex_fixed"]
        )
    )
    subset=["Category","Year","Technology","capex_energy","capex_power","capex_fixed","TotalCapexEur"]
    subset_df=df[subset]
    
    return subset_df


def residual_value_calculator(a:float, b:float,df_master: pd.DataFrame,T:float)->pd.DataFrame:
    
    """
    So the simplest recommendation is:
    Diesel / HVO: a = 1.0, b = 0.26
    BEV today: a = 1.0, b = 0.32
    BEV future / optimistic: a = 1.0, b = 0.22
    FCV today: a = 1.0, b = 0.32
    H2-ICE: a = 1.0, b = 0.24
        """
   
    df = df_master.copy()
    # Compute annual driver cost
    df["ResidualValueEur"] = df["TotalCapexEur"] * a
    df["ResidualValuePct"] = a * np.exp(-b * T)
    # Residual value in currency
    df["ResidualValueEur"] = df["TotalCapexEur"] * df["ResidualValuePct"]
    df["ResidualValueEur"] = df["ResidualValueEur"].astype(int)
    df["ResidualValuePct"]=round(df["ResidualValuePct"],3)
    return df
    

def insurance_calculator(df_master: pd.DataFrame,f:float=0.05):
    df = df_master.copy()
    df["InsuranceCostEur"]=df["ResidualValueEur"]*f
    df["InsuranceCostEur"]=df["InsuranceCostEur"].astype(int)
    return df


def maintenance_calculator(df_master:pd.DataFrame, df_main:pd.DataFrame):
    df = df_master.copy()
    df = df.merge(
            df_main[["Category", "Technology", "Year" ,"MaintenanceCostEurKm"]],
            on=["Category", "Technology", "Year"],
            how="left",
)
    df["MaintenanceCostEur"]=df["MaintenanceCostEurKm"]*df["YearlyMileageKm"]
    return df



   
def consumption_calculator(GCW: float, coefficients: dict) -> pd.DataFrame:
    rows = []
    for tech, vals in coefficients.items():
        cons = vals["A"] * np.log(GCW *1000) + vals["B"]

        rows.append({
            "Technology": tech,
            "GCW [t]": GCW,
            "Consumption": round(cons, 3),
            "Unit": vals["unit"],
            "Value_LDE_100km": round(cons / vals["lde"] * 100, 2)
        })
    return pd.DataFrame(rows)


def tco_yearly_fuel_cost_calculator(
    df_consumption,
    diesel_price,
    lng_price,
    electricity_price,
    h2_price,
    yearly_mileage
):
    df = df_consumption.copy()

    # Scale consumption to user mileage
    df["consumption_per_km"] = df["FuelConsumption"] / 100.0
    df["Annual_consumption_user"] = df["consumption_per_km"] * yearly_mileage

    # Direct multiplication based on Technology
    df["AnnualFuelCostEur"] = 0.0

    df.loc[df["Technology"] == "ICE-D", "AnnualFuelCostEur"] = \
        df["Annual_consumption_user"] * diesel_price

    df.loc[df["Technology"] == "ICE-NG", "AnnualFuelCostEur"] = \
        df["Annual_consumption_user"] * lng_price

    df.loc[df["Technology"] == "BET", "AnnualFuelCostEur"] = \
        df["Annual_consumption_user"] * electricity_price

    df.loc[df["Technology"] == "FCET", "AnnualFuelCostEur"] = \
        df["Annual_consumption_user"] * h2_price

    return df





def tco_consumption_calculator(GCW: float, coefficients: dict,mileage) -> pd.DataFrame:
    rows = []
    for tech, vals in coefficients.items():
        cons = vals["A"] * np.log(GCW *1000) + vals["B"]
        rows.append({
            "Technology": tech,
            "GCW [t]": GCW,
            "Consumption": round(cons, 3),
            "Unit": vals["unit"],
            "Value_LDE_100km": round(cons / vals["lde"] * 100, 2),
            "Annual_consumption": round(cons * mileage, 2)
            
        })
    
    
    return pd.DataFrame(rows)


def driver_wages_calculator(df_master: pd.DataFrame, df_wages: pd.DataFrame):

    df = df_master.copy()

    # Merge on Country + Year
    df = df.merge(
        df_wages[["Country", "Year", "Unitary_Wage_km"]],
        on=["Country", "Year"],
        how="left"
    )

    # Compute annual driver cost
    df["AnnualDriverCostEur"] = df["Unitary_Wage_km"] * df["YearlyMileageKm"]

    return df



def tco_calculator(i: float, T: int, df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simplified annual TCO in EUR/km using an Equivalent Annual Cost approach.

    Inputs
    ------
    i : float
        Discount rate in %, e.g. 5 for 5%
    T : int
        Ownership period in years
    df : pd.DataFrame
        Must contain:
        - TotalCapexEur           [EUR]
        - ResidualValueEur        [EUR]
        - annual_km_user        [km/year]
        - AnnualFuelCostEur      [EUR/year]
        - AnnualTollCostEur      [EUR/year]
        - AnnualDriverCostEur    [EUR/year]
        - MaintenanceCostEur       [EUR/km]   or annual maintenance if adapted below

    Returns
    -------
    pd.DataFrame
        Adds:
        - TCO_CAPEX_EUR_per_km
        - TCO_FUEL_EUR_per_km
        - TCO_TOLL_EUR_per_km
        - TCO_WAGES_EUR_per_km
        - TCO_MAINT_EUR_per_km
        - TCO_TOTAL_EUR_per_km
    """

    out = df.copy()
    i = i / 100  # convert % to decimal

    # Required columns
    numeric_cols = [
        "TotalCapexEur",
        "ResidualValueEur",
        "YearlyMileageKm",
        "AnnualFuelCostEur",
        "AnnualTollCostEur",
        "AnnualDriverCostEur",
        "MaintenanceCostEur",
        "ETSCO2CostEur"
    ]

    for c in numeric_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    # Avoid division by zero
    out["YearlyMileageKm"] = out["YearlyMileageKm"].replace(0, np.nan)
    # Capital Recovery Factor
    if i == 0:
        crf = 1 / T
        pv_residual_factor = 1.0
    else:
        crf = (i * (1 + i) ** T) / (((1 + i) ** T) - 1)
        pv_residual_factor = 1 / ((1 + i) ** T)

    out["CRF"] = crf

    # Annualized CAPEX net of discounted residual value
    out["TCO_CAPEX_EUR"] = (out["TotalCapexEur"] - out["ResidualValueEur"] * pv_residual_factor) * crf
    out["TCO_CAPEX_EUR_per_km"] = out["TCO_CAPEX_EUR"] / out["YearlyMileageKm"]

    # Annual operating costs: no discounting in annual view
    out["TCO_FUEL_EUR_per_km"] = out["AnnualFuelCostEur"] / out["YearlyMileageKm"]
    out["TCO_TOLL_EUR_per_km"] = out["AnnualTollCostEur"] / out["YearlyMileageKm"]
    out["TCO_WAGES_EUR_per_km"] = out["AnnualDriverCostEur"] / out["YearlyMileageKm"]

    # MaintenanceCostEur assumed to be already in EUR/km
    out["TCO_MAINT_EUR_per_km"] = out["MaintenanceCostEur"]/out["YearlyMileageKm"]

    # ETS CO2 costs
    out["TCO_ETS_CO2_per_km"] = out["ETSCO2CostEur"]/out["YearlyMileageKm"]

    # Total
    out["TCO_TOTAL_EUR_per_km"] = (
        out["TCO_CAPEX_EUR_per_km"]
        + out["TCO_FUEL_EUR_per_km"]
        + out["TCO_TOLL_EUR_per_km"]
        + out["TCO_WAGES_EUR_per_km"]
        + out["TCO_MAINT_EUR_per_km"]
        +out["TCO_ETS_CO2_per_km"]
    )

    return out