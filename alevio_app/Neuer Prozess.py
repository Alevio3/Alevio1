# Beispiel-Funktion für pages.py
import streamlit as st
import pandas as pd

def daten_upload():
    st.title("Event-Log Upload")
    uploaded_file = st.file_uploader("Wähle eine Event-Log Datei (CSV oder Excel):", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("Datei erfolgreich geladen!")
        st.dataframe(df.head())

        # Spaltenauswahl für Case ID, Activity, Timestamp
        st.subheader("Spaltenauswahl")
        case_col = st.selectbox("Case ID Spalte:", df.columns)
        activity_col = st.selectbox("Activity Spalte:", df.columns)
        timestamp_col = st.selectbox("Timestamp Spalte:", df.columns)

        # Beispiel: Auswahl speichern oder weiterverarbeiten
        if st.button("Übernehmen"):
            st.write("Ausgewählte Spalten:")
            st.write(f"Case ID: {case_col}")
            st.write(f"Activity: {activity_col}")
            st.write(f"Timestamp: {timestamp_col}")
            # Hier kannst du die Daten weiterverarbeiten (z.B. für Mining-Algorithmen)