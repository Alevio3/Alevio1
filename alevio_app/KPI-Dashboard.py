import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def kpi_dashboard():
    st.header('KPI Dashboard')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return
    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    activity_col = st.session_state.get('activity_col', df.columns[1])
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    prozess_dauern = df.groupby(case_col).agg({timestamp_col: ['min', 'max']})
    prozess_dauern['Lead Time'] = (prozess_dauern[(timestamp_col, 'max')] - prozess_dauern[(timestamp_col, 'min')]).dt.total_seconds() / 86400
    lead_time_avg = prozess_dauern['Lead Time'].mean()
    st.metric("Ø Lead Time (Tage)", f"{lead_time_avg:.2f}")
    st.bar_chart(prozess_dauern['Lead Time'])