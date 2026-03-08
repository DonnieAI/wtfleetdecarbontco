import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

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

#------------------------DATA EXTRACTION-----------------------------------------------------
# 1. Read CSV with 2 header rows
df_raw = pd.read_csv("data/LDT_ACEA_registration.csv", header=[0, 1])
# Set country as index and keep only the numeric data under a MultiIndex (powertrain, year)
df = df_raw.set_index(('country', 'country'))
# 2. Stack + melt -> long format: country, powertrain, year, registrations
df_long = (
    df
    .stack(0)  # stack powertrain (level 0 of columns) into the index
    .rename_axis(index=['country', 'powertrain'])
    .reset_index()                  # columns: country, powertrain, 2025, 2024, 2023
    .melt(
        id_vars=['country', 'powertrain'],
        var_name='year',
        value_name='registrations'
    )
)

# Clean types
df_long['year'] = df_long['year'].astype(int)
df_long['registrations'] = pd.to_numeric(df_long['registrations'], errors='coerce').fillna(0)

df_long = df_long[df_long['powertrain'].isin(['EV', 'HYBRID', 'OTHERS', 'PETROL', 'DIESEL'])]


powertrain_order = ['DIESEL','PETROL','HYBRID','EV' ,'OTHERS']
latest_year = int(sorted(df_long["year"].unique())[-1])

# 2. Filter only latest year
df_latest = df_long[df_long["year"] == latest_year].copy()

# 3. Remove aggregate regions
excluded_regions = ["EU", "EU + EFTA + UK"]
df_latest = df_latest[~df_latest["country"].isin(excluded_regions)]

# 4. Compute total registrations per country for sorting
totals = (
        df_latest.groupby("country")["registrations"]
        .sum()
        .reset_index()
        .rename(columns={"registrations": "total_regs"})
)

# Sort descending by total registrations
sorted_countries = totals.sort_values("total_regs", ascending=True)["country"].tolist()

# 5. Pivot for plotting (wide form)
df_plot = df_latest.pivot_table(
            index="country",
            columns="powertrain",
            values="registrations",
            aggfunc="sum",
            fill_value=0
        ).reindex(sorted_countries)

# ------------------------------------------------------------
# Streamlit output
# ------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------
st.title(f"NEW {SEGMENT} REGISTRATIONS")
st.markdown(f"""
### New {SEGMENT} Registrations | Light commercial vehicles up to 3.5 t
""")
st.markdown("""
Source: ACEA
""")

# ------------------------------------------------------------
# Create horizontal stacked bar figure
# ------------------------------------------------------------
fig1 = go.Figure()

for pt in powertrain_order:
    if pt in df_plot.columns:
        fig1.add_trace(
            go.Bar(
                y=df_plot.index,
                x=df_plot[pt],
                name=pt,
                orientation="h",
                marker_color=color_map[pt]
            )
        )

fig1.update_layout(
    barmode="stack",
    height=900,
    title=f"LDT Registrations by Powertrain - {latest_year}",
    xaxis_title="Registrations",
    yaxis_title="Country",
    legend_title="Powertrain",
)


st.plotly_chart(fig1, use_container_width=True)


#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------


st.title(f"{SEGMENT} Registrations - Stacked by Powertrain")

countries = sorted([c for c in df_long['country'].unique() if c not in excluded_regions])
if not countries:
    st.warning("No country-level data available to display.")
    st.stop()

default_index = countries.index("Italy") if "Italy" in countries else 0
selected_country = st.selectbox("Select country", countries, index=default_index)

d = df_long[df_long['country'] == selected_country]

#powertrain_order = ['EV', 'HYBRID', 'OTHERS', 'PETROL', 'DIESEL']

# Colors assigned already:
# color_map = { 'EV': ..., 'HYBRID': ..., ... }
# Powertrains used ONLY for the share line plot (bottom subplot)
share_powertrains = ['EV', 'HYBRID', 'OTHERS', 'PETROL']   # diesel removed

# Compute TOTAL per year for the selected country
total_df = (
    d.groupby("year")["registrations"].sum()
    .reset_index()
    .rename(columns={"registrations": "total_regs"})
)

# Merge total into d
d2 = d.merge(total_df, on="year", how="left")

# Compute share percentage
d2["share_pct"] = (d2["registrations"] / d2["total_regs"].replace(0, pd.NA)) * 100
d2["share_pct"] = d2["share_pct"].fillna(0)

# Ensure years are integers
d2["year"] = d2["year"].astype(int)

#color_map = {pt: palette_blue[i % len(palette_blue)] for i, pt in enumerate(powertrain_order)}

# =====================================================
# Create subplot structure
# =====================================================
fig2 = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.10,
    subplot_titles=(
        f"{SEGMENT} Registrations in {selected_country} by Powertrain",
        f"{SEGMENT} Powertrain Share [%] of Total Registrations in {selected_country}"
    ),
    row_heights=[0.65, 0.35]
)

# =====================================================
# TOP SUBPLOT: STACKED ABSOLUTE VALUES
# =====================================================
for pt in powertrain_order:
    if pt in d2['powertrain'].unique():
        sub = d2[d2['powertrain'] == pt].sort_values("year")
        fig2.add_trace(
            go.Bar(
                x=sub["year"],
                y=sub["registrations"],
                name=pt,
                marker_color=color_map[pt],
            ),
            row=1, col=1
        )

# =====================================================
# BOTTOM SUBPLOT: POWERTRAIN SHARE (% of TOTAL)
# =====================================================
# BOTTOM SUBPLOT: Share (%) AS LINE PLOT
for pt in share_powertrains:
    if pt in d2["powertrain"].unique():
        sub = d2[d2["powertrain"] == pt].sort_values("year")

        fig2.add_trace(
            go.Scatter(
                x=sub["year"],
                y=sub["share_pct"],
                name=pt + " share",
                mode="lines+markers",

                # --- Line style ---
                line=dict(
                    width=2,
                    dash="dash",          # dashed line
                    color=color_map[pt]
                ),

                # --- Marker style ---
                marker=dict(
                    symbol="diamond",     # diamond shape
                    size=14,              # bigger markers
                    color=color_map[pt],
                    line=dict(width=1.1, color="black")   # optional elegant outline
                ),

                showlegend=False,
            ),
            row=2,
            col=1
        )

# =====================================================
# LAYOUT FIXES
# =====================================================
fig2.update_layout(
    barmode="stack",  # stacked bars for both plots
    height=800,
    legend_title="Powertrain",
)

# Ensure integer year axis
fig2.update_xaxes(
    tickmode="linear",
    dtick=1,
    tickformat=".0f",
    title="Year",
    row=2, col=1
)

# Main y-axes titles
fig2.update_yaxes(title="Registrations", row=1, col=1)
fig2.update_yaxes(title="Share (%)", tickformat=".1f", row=2, col=1)


# STREAMLIT OUTPUT
st.plotly_chart(fig2, use_container_width=True)



