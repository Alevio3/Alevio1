import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

def login():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.5rem;'>Alevio Login</h1>
        <p style='color:#222;font-size:1.1rem;'>Bitte melden Sie sich mit Ihren Zugangsdaten an.</p>
    """, unsafe_allow_html=True)
    username = st.text_input("Benutzername", placeholder="z.B. max.mustermann")
    password = st.text_input("Passwort", type="password", placeholder="Passwort")
    if st.button("Login", use_container_width=True):
        st.success(f"Willkommen, {username}!")

def homescreen():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>Willkommen bei Alevio</h1>
        <p style='color:#222;font-size:1.1rem;'>Wählen Sie eine Aktion:</p>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("<span style='font-size:1.2rem;font-weight:600;'>Projekt anlegen</span>", use_container_width=True, key="projekt", help="Neues Projekt anlegen", type="primary"):
            st.session_state['projekt_anlegen'] = True
    with col2:
        if st.button("<span style='font-size:1.2rem;font-weight:600;'>Bestehende Prozesse</span>", use_container_width=True, key="bestehend", help="Bestehende Projekte ansehen"):
            st.session_state['projekt_anlegen'] = False

def projekt_anlegen():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>Neues Projekt anlegen</h1>
        <p style='color:#222;font-size:1.1rem;'>Bitte geben Sie die Projektdetails ein und laden Sie Ihre CSV-Datei hoch.</p>
    """, unsafe_allow_html=True)
    department = st.selectbox("Department wählen", ["HR", "IT", "Finance", "Produktion"])
    team = st.text_input("Team", placeholder="z.B. Data Science")
    prozessname = st.text_input("Prozessname", placeholder="z.B. Onboarding-Prozess")
    uploaded_file = st.file_uploader("CSV Datei hochladen", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("<b>Vorschau der Daten:</b>", unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
            case_id = st.selectbox("Case-ID Spalte", df.columns)
            activity = st.selectbox("Activity Spalte", df.columns)
            ts_start = st.selectbox("Timestamp Start Spalte", df.columns)
            ts_end = st.selectbox("Timestamp End Spalte", df.columns)
            if st.button("Projekt speichern", use_container_width=True, type="primary"):
                # Projektordner anlegen
                os.makedirs("projekte", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                project_id = f"{prozessname}_{timestamp}".replace(" ", "_")
                # CSV speichern
                csv_path = f"projekte/{project_id}.csv"
                df.to_csv(csv_path, index=False)
                # Metadaten speichern
                meta = {
                    "department": department,
                    "team": team,
                    "prozessname": prozessname,
                    "case_id": case_id,
                    "activity": activity,
                    "ts_start": ts_start,
                    "ts_end": ts_end,
                    "csv_path": csv_path,
                    "created_at": timestamp
                }
                with open(f"projekte/{project_id}.json", "w") as f:
                    json.dump(meta, f, indent=2)
                st.success("Projekt gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Einlesen der Datei: {e}")

def prozessvisualisierung():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>Prozessvisualisierung</h1>
    """, unsafe_allow_html=True)
    st.info("Hier könnte eine Prozessvisualisierung erscheinen. (z.B. Graph mit Plotly/Graphviz)")

def prozesseffizienz():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>Prozesseffizienz</h1>
    """, unsafe_allow_html=True)
    st.info("Hier könnten Effizienzmetriken angezeigt werden. (z.B. Durchlaufzeiten, Bottlenecks)")

def kpi_dashboard():
    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>KPI Dashboard</h1>
    """, unsafe_allow_html=True)
    st.info("Hier könnten KPIs visualisiert werden. (z.B. Balkendiagramme, Kennzahlen)")

def control_center():
    st.sidebar.title("Alevio Sidebar")
    st.sidebar.info("Hier kannst du Filter, Einstellungen oder Navigationselemente einbauen.")

    st.markdown("""
        <h1 style='color:#0057FF;font-weight:800;font-size:2.2rem;'>Control Center</h1>
        <p style='color:#222;font-size:1.1rem;'>Wähle eine Aktion:</p>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Meine Projekte", use_container_width=True, type="primary"):
            st.session_state['view'] = 'meine_projekte'
    with col2:
        if st.button("Neuen Prozess anlegen", use_container_width=True):
            st.session_state['view'] = 'neuer_prozess'

    # Beispielhafte Navigation
    if st.session_state.get('view') == 'meine_projekte':
        st.info("Hier werden später deine Projekte angezeigt.")
    elif st.session_state.get('view') == 'neuer_prozess':
        st.info("Hier kannst du einen neuen Prozess anlegen.")
