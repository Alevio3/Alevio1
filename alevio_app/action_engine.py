import streamlit as st
import pandas as pd

def action_engine():
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        st.stop()
    # ... restlicher Code ...