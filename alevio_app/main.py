import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from alevio_app import pages

st.set_page_config(page_title="Alevio Process Mining", layout="wide")

# Logo einbinden (lokal im assets-Ordner)
st.image("alevio_app/assets/Logo.png", width=180)

st.sidebar.title("Alevio Navigation")
page = st.sidebar.radio("Seite wählen:", (
    "Log-In",
    "Control Center",
    "Handlungsempfehlung",
    "KPI-Dashboard",
    "Neuer Prozess",
    "Prozesseffizienz",
    "Prozessvisualisierung"
))

if page == "Log-In":
    pages.login()
elif page == "Control Center":
    pages.control_center()
elif page == "Handlungsempfehlung":
    pages.handlungsempfehlung()
elif page == "KPI-Dashboard":
    pages.kpi_dashboard()
elif page == "Neuer Prozess":
    pages.neuer_prozess()
elif page == "Prozesseffizienz":
    pages.prozesseffizienz()
elif page == "Prozessvisualisierung":
    pages.prozessvisualisierung()
