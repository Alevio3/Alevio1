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

    if 'df' in st.session_state:
        df = st.session_state['df']
        st.dataframe(df.head(20))
        columns = list(df.columns)

        # Vorauswahl-Logik
        def find_col(possibles, fallback_idx):
            for p in possibles:
                for c in columns:
                    if p.lower() in c.lower():
                        return columns.index(c)
            return fallback_idx

        case_idx = find_col(["case", "fall", "id"], 0)
        activity_idx = find_col(["activity", "aktivität"], 1)
        ts_start_idx = find_col(["start", "begin"], 2)
        ts_end_idx = find_col(["end", "ende", "finish", "abschluss"], len(columns)-1)

        case_col = st.selectbox("Fall-ID Spalte auswählen", columns, index=case_idx, key="case_col")
        activity_col = st.selectbox("Aktivitätsspalte auswählen", columns, index=activity_idx, key="activity_col")
        timestamp_start_col = st.selectbox("Zeitstempel Start", columns, index=ts_start_idx, key="timestamp_col_start")
        timestamp_end_col = st.selectbox("Zeitstempel Ende", columns, index=ts_end_idx, key="timestamp_col_end")

        st.info("Wählen Sie die passenden Spalten aus und klicken Sie dann auf **Weiter**.")
    else:
        st.info("Bitte laden Sie eine CSV-Datei hoch, um fortzufahren.")

    st.sidebar.markdown(f"**Schritt {st.session_state['page_idx']+1} von {len(PAGES)}:** {PAGES[st.session_state['page_idx']]}")

    if st.button("Weiter", key="weiter_upload"):
        # Speichere Auswahl erst jetzt!
        st.session_state['case_col'] = st.session_state['case_col']
        st.session_state['activity_col'] = st.session_state['activity_col']
        st.session_state['timestamp_col'] = st.session_state['timestamp_col_start']
        st.session_state['timestamp_end_col'] = st.session_state['timestamp_col_end']
        st.session_state['page_idx'] += 1
        st.rerun()

