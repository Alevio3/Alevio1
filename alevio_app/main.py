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
    "Login",
    "Homescreen",
    "Projekt anlegen",
    "Prozessvisualisierung",
    "Prozesseffizienz",
    "KPI Dashboard"
))

if page == "Login":
    pages.login()
elif page == "Homescreen":
    pages.homescreen()
elif page == "Projekt anlegen":
    pages.projekt_anlegen()
elif page == "Prozessvisualisierung":
    pages.prozessvisualisierung()
elif page == "Prozesseffizienz":
    pages.prozesseffizienz()
elif page == "KPI Dashboard":
    pages.kpi_dashboard()
