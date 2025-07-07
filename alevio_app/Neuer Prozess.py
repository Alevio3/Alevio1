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

def upload_csv():
    st.header('CSV-Daten hochladen')
    uploaded_file = st.file_uploader('CSV-Datei hochladen', type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        st.success(f'Datei {uploaded_file.name} erfolgreich geladen!')
        st.dataframe(df.head(20))
        columns = list(df.columns)
        dropdown_labels = ["Case-ID", "Aktivität", "Startzeit", "Endzeit"]
        selected_cols = []
        for i in range(4):
            label = dropdown_labels[i] if i < len(dropdown_labels) else f"Spalte {i+1} auswählen"
            col = st.selectbox(label, columns, key=f'csv_col_{i}')
            selected_cols.append(col)
        st.session_state['case_col'] = selected_cols[0]
        st.session_state['activity_col'] = selected_cols[1]
        st.session_state['timestamp_col'] = selected_cols[2]
        st.info(f"Ausgewählte Spalten: {', '.join(selected_cols)}")
        if st.button('Weiter'):
            st.session_state['goto_nav'] = '🔎 Prozessvisualisierung'
            st.rerun()
    else:
        st.info('Bitte laden Sie eine CSV-Datei hoch, um fortzufahren.')