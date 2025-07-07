import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from login import login
from upload_csv import upload_csv
from prozessvisualisierung import prozessvisualisierung
from kpi_dashboard import kpi_dashboard
from bottleneck_analyse import bottleneck_analyse
from action_engine import action_engine
from simulation import simulation
from administration import administration

st.set_page_config(page_title="Alevio Process Mining", layout="wide")

# Logo oben in die Sidebar einfügen
with st.sidebar:
    st.image("assets/Logo.png", width=220)  # <- Hier die Größe anpassen
    st.markdown("---")

PAGES = [
    "Daten hochladen",
    "Prozessvisualisierung",
    "KPI Dashboard",
    "Bottleneck Analyse",
    "Handlungsempfehlungen",
    "Simulation",
    "Administration"
]

def main():
    if 'page_idx' not in st.session_state:
        st.session_state['page_idx'] = 0

    st.session_state['PAGES'] = PAGES

    # LOGOUT-BUTTON (optional)
    if 'logged_in_user' in st.session_state:
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", type="primary"):
            del st.session_state['logged_in_user']
            st.rerun()

    # LOGIN
    if 'logged_in_user' not in st.session_state:
        st.sidebar.title("Navigation")
        st.sidebar.info("Bitte zuerst einloggen.")
        login()
        return

    # Seiten-Navigation per Index
    page_idx = st.session_state['page_idx']
    nav = PAGES[page_idx]
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Aktuelle Seite: **{nav}**")

    selected = st.sidebar.radio("Navigation", PAGES, index=st.session_state['page_idx'])
    if selected != PAGES[st.session_state['page_idx']]:
        st.session_state['page_idx'] = PAGES.index(selected)
        st.rerun()

    # Seiteninhalt anzeigen
    if nav == 'Daten hochladen':
        upload_csv()
    elif nav == 'Prozessvisualisierung':
        prozessvisualisierung()
    elif nav == 'KPI Dashboard':
        kpi_dashboard()
    elif nav == 'Bottleneck Analyse':
        bottleneck_analyse()
    elif nav == 'Handlungsempfehlungen':
        action_engine()
    elif nav == 'Simulation':
        simulation()
    elif nav == 'Administration':
        administration()

    # Weiter/Zurück Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück", disabled=page_idx == 0):
            st.session_state['page_idx'] = max(0, page_idx - 1)
            st.rerun()
    with col2:
        if st.button("Weiter", key="weiter_main", disabled=page_idx == len(PAGES) - 1):
            st.session_state['page_idx'] = min(len(PAGES) - 1, page_idx + 1)
            st.rerun()

if __name__ == "__main__":
    main()
