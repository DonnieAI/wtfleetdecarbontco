import streamlit as st

def apply_style_and_logo():
    # Apply custom font style
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat&display=swap');
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar content
    with st.sidebar:
        # App name at top
        st.markdown("<h2 style='text-align: center;'>WT APPLICATIONS HUB", unsafe_allow_html=True)
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        st.image("logo-wavetransition_long.png", use_container_width=True)