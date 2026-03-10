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


st.title(f"🚚  POLICIES OVERVIEW - IT")
st.markdown(f"""
### 📈 Policies impact on TCO elements 
""")
st.markdown("""
Source: Wavestransition elaboration
""")


policy_to_tco_map = {
    # capex-related
    "HDV CO₂ Emission Standards": ["capex"],
    "Euro 7 Emission Standards": ["capex"],
    "Batteries Directive / Regulation": ["capex"],

    # Fuel Costs
    "Renewable Energy Directive": ["Fuel Costs"],
    "Fuel Quality Directive": ["Fuel Costs"],
    "Energy Efficiency Directive": ["Fuel Costs"],

    # Infrastructure
    "Alternative Fuels Infrastructure Regulation (AFIR)": ["Charging Infrastructure", "capex"],
    "TEN-T Regulation": ["Charging Infrastructure"],

    # Tolls
    "Eurovignette Directive": ["Tolls"],

    # CO₂ Price
    "EU ETS Directive": ["CO₂ Price"],
    "ETS for buildings, road transport, and additional sectors": ["CO₂ Price"],

    # Maintenance / Driver Wages
    "Driving Time and Rest Periods": ["Driver Wages"],
    "Directive on Maximum Authorized Weights and Dimensions": ["O&M", "capex"],

    # subvenstions
    "Social Climate Fund": ["subvenstions"],
    "Horizon Europe": ["subvenstions"],
    "Just Transition Fund": ["subvenstions"],
    "Recovery and Resilience Facility (RRF)": ["subvenstions"],
    "Alternative Fuels Infrastructure Facility (AFIF)": ["subvenstions", "capex"],

    # residual value
    "Clean Vehicles Directive (CVD)": ["residual value"],


    # GENERAL (could impact multiple TCO elements)
    "Effort Sharing Regulation": ["capex", "Fuel Costs", "CO₂ Price"]
}

# Create label list and mapping
label_set = set()
for policy, tco_components in policy_to_tco_map.items():
    label_set.add(policy)
    label_set.update(tco_components)

labels = list(label_set)
label_index = {label: idx for idx, label in enumerate(labels)}

source, target, value = [], [], []

for policy, tco_components in policy_to_tco_map.items():
    for tco in tco_components:
        source.append(label_index[policy])
        target.append(label_index[tco])
        value.append(1)  # Or adjust by importance

# Define source and target indices
#source = [0, 1, 2, 1]
#target = [3, 3, 4, 4]
#value = [1, 1, 1, 1]  # All weights 1 for now

#labels[:5], source[:5], target[:5], value[:5]

# Sankey diagram
fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value
                )
            )])



fig.add_annotation(
                text="EU Policies",
                x=0.01,  # near left
                y=1.05,
                showarrow=False,
                font=dict(size=22, color=palette_other[1])
            )

fig.add_annotation(
                text="TCO Components",
                x=0.99,  # near right
                y=1.05,
                showarrow=False,
                font=dict(size=22, color=palette_other[4]),
                xanchor="right"
            )

fig.update_layout(
        yaxis=dict(
            #categoryorder='array',
            #categoryarray=["HDT", "MDT", "LDT"],
            color="white",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        xaxis=dict(
            color="white",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        font=dict(
            size=14,
            color=palette_other[1]
        ),
        paper_bgcolor="#005680",
        plot_bgcolor="#005680",
        bargap=0.2,
        height=900,
        #legend_title="Year"
    )


st.plotly_chart(fig, use_container_width=True)