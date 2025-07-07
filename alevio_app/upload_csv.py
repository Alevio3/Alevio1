import streamlit as st
import pandas as pd

PAGES = [
    "Daten hochladen",
    "Prozessvisualisierung",
    "KPI Dashboard",
    "Bottleneck Analyse",
    "Handlungsempfehlungen",
    "Simulation",
    "Administration"
]

def upload_csv():
    st.header('CSV-Daten hochladen')
    uploaded_file = st.file_uploader('CSV-Datei auswählen', type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state['df'] = df
        st.success(f'Datei {uploaded_file.name} erfolgreich geladen!')
    # Zeige die Auswahlfelder, wenn eine Datei im Session State ist
    if 'df' in st.session_state:
        df = st.session_state['df']
        st.dataframe(df.head(20))
        columns = list(df.columns)
        case_col = st.selectbox("Case-ID Spalte auswählen", columns, key="case_col")
        activity_col = st.selectbox("Aktivitäts-Spalte auswählen", columns, key="activity_col")
        timestamp_col = st.selectbox("Zeitstempel-Spalte auswählen", columns, key="timestamp_col")
        st.info("Wählen Sie die passenden Spalten aus und klicken Sie dann auf **Weiter**.")
    else:
        st.info("Bitte laden Sie eine CSV-Datei hoch, um fortzufahren.")

    st.sidebar.markdown(f"**Schritt {st.session_state['page_idx']+1} von {len(PAGES)}:** {PAGES[st.session_state['page_idx']]}")
    
    if st.button("Weiter", key="weiter_upload"):
        st.session_state['page_idx'] += 1
        st.rerun()

