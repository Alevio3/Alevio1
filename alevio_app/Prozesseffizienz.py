import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def bottleneck_analyse():
    st.header('Bottleneck Analyse')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return
    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    activity_col = st.session_state.get('activity_col', df.columns[1])
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    df = df.sort_values([case_col, timestamp_col])
    df['next_activity'] = df.groupby(case_col)[activity_col].shift(-1)
    df['next_timestamp'] = df.groupby(case_col)[timestamp_col].shift(-1)
    df['duration'] = (df['next_timestamp'] - df[timestamp_col]).dt.total_seconds() / 3600
    df_valid = df.dropna(subset=['next_activity', 'duration'])
    stats = df_valid.groupby(activity_col)['duration'].mean().sort_values(ascending=False)
    st.bar_chart(stats)
    st.info('Die Aktivität mit der höchsten durchschnittlichen Verweildauer ist der größte Engpass (Bottleneck) im Prozess.')