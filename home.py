"""
FLEET DECARB TCO

"""
#cdm
#     projenv\Scripts\activate
#     streamlit run home.py

import streamlit as st
import pandas as pd


# ✅ Must be the first Streamlit call
st.set_page_config(
    page_title="Home",   # Browser tab title
    page_icon="🏠",      # Optional favicon (emoji or path to .png/.ico)
    layout="wide"        # "centered" or "wide"
)


# ── Load user credentials and profiles ────────────────────────
CREDENTIALS = dict(st.secrets["auth"])
PROFILES = st.secrets.get("profile", {})

# ── Login form ────────────────────────────────────────────────
def login():
    st.title("🔐 Login Required")

    user = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")

    if st.button("Login", key="login_button"):
        if user in CREDENTIALS and password == CREDENTIALS[user]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = user
            st.session_state["first_name"] = PROFILES.get(user, {}).get("first_name", user)
        else:
            st.error("❌ Invalid username or password")

# ── Auth state setup ──────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ── Login gate ────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    login()
    st.stop()

# ── App begins after login ────────────────────────────────────

# ---------------Sidebar
from utils import apply_style_and_logo

st.sidebar.success(f"Welcome {st.session_state['first_name']}!")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update(authenticated=False))

# Spacer to push the link to the bottom (optional tweak for better placement)
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# Company website link
st.sidebar.markdown(
    '<p style="text-align:center;">'
    '<a href="https://www.wavetransition.com" target="_blank">🌐 Visit WaveTransition</a>'
    '</p>',
    unsafe_allow_html=True
)
# ---------Main content
st.title("**FLEET DECARB TCO**")

# --- Centered cover image ---
from PIL import Image
cover_img = Image.open("cover.png")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(cover_img, use_container_width=False, width=800)  # updated
#st.image(cover_img, use_container_width=True)  # auto fit


st.markdown("""
## WAVETRANSITION – HEAVY-DUTY FLEET DECARBONIZATION TCO PLATFORM  

**Fleet Decarb TCO** is an interactive analytics tool designed to **compare the Total Cost of Ownership (TCO)** of different **decarbonization pathways for heavy-duty vehicle fleets in Europe**.

The app focuses on medium- and long-haul operations and enables users to **benchmark today’s diesel baseline** against alternative powertrains and fuels, such as:

- **Biofuels / drop-in fuels** (HVO, advanced biodiesel)  
- **Gas options** (CNG, LNG, bio-CNG, bio-LNG)  
- **Battery-electric trucks (BEV)**  
- **Hydrogen fuel cell trucks (FCEV)**  
- **Emerging e-fuels and synthetic fuels**  

By integrating **vehicle, fuel, infrastructure and policy parameters** into a consistent TCO framework, Fleet Decarb TCO supports evidence-based decisions on **when**, **where** and **how** to decarbonize heavy-duty fleets.

---

### 🚚 Scope & Coverage

The platform is tailored to the **European heavy-duty road freight context**, with a focus on:

- **Fleet use cases**: regional and long-haul trucking, distribution, and specialized applications  
- **Cost components**:
  - Vehicle CAPEX (purchase, financing, residual value)  
  - Energy / fuel costs (€/kWh, €/kg, €/litre with efficiency effects)  
  - Infrastructure costs (depot charging, public fast charging, refuelling stations)  
  - O&M, tires, insurance, tolls and other operating costs  
  - CO₂-related elements (carbon prices, incentives, tax shifts where applicable)  
- **Geographical dimension**: comparison across **EU countries and regions**, reflecting differences in energy prices, taxation and policy support.

---

### 🎯 Purpose

The goal of **Fleet Decarb TCO** is to provide **a transparent, harmonized view of the economics of fleet decarbonization**, helping:

- Fleet operators understand the **cost implications of each technology choice**  
- OEMs and suppliers discuss **total-cost competitiveness** with customers  
- Investors and infrastructure players evaluate **business cases for charging and refuelling**  
- Policymakers explore **policy levers and cost gaps** between low-carbon options and diesel

Typical questions the tool can support include:

- *When does a battery-electric truck become TCO-competitive versus diesel for my duty cycle?*  
- *What is the TCO impact of bio-LNG vs HVO vs hydrogen on long-haul routes?*  
- *How sensitive are results to energy prices, carbon prices or utilization rates?*  

---

### 📌 Key Features

- **Scenario-based TCO comparison** across multiple technologies and fuels  
- **Configurable duty cycles** (annual mileage, load factor, route type, lifetime)  
- **Detailed cost breakdowns** (CAPEX, OPEX, energy, infrastructure, CO₂) per vehicle and per km  
- **Country-specific assumptions** for energy prices and fiscal parameters  
- **Interactive charts and tables** to visualize cost drivers and sensitivities  

---

### ⚠️ Important Note

The results are intended as a **decision-support and exploration tool**, not as a substitute for **project-specific engineering or financial models**.  
Underlying assumptions (prices, efficiencies, lifetime, incentives, etc.) should always be reviewed and adjusted to reflect **real-world fleet conditions**.

---

### 🧭 Start Exploring

Use the navigation menu to:

- Select **fleet profiles and duty cycles**  
- Configure **technology / fuel scenarios**  
- Inspect **TCO breakdowns and sensitivities** across countries and options  

and build a **clear, comparable picture of your heavy-duty fleet decarbonization pathways in Europe**.
""")


