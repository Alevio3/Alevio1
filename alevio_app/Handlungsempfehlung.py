import streamlit as st
import pandas as pd

def action_engine():
    st.header('Handlungsempfehlungen')
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
    df['next_time'] = df.groupby(case_col)[timestamp_col].shift(-1)
    df['duration'] = (df['next_time'] - df[timestamp_col]).dt.total_seconds() / 60
    bottlenecks = df.groupby(activity_col)['duration'].mean().dropna().sort_values(ascending=False)
    if not bottlenecks.empty:
        top_bottleneck = bottlenecks.index[0]
        st.warning(f"Engpass erkannt: Die Aktivität '{top_bottleneck}' ist ein potenzieller Flaschenhals.")
        st.info(f"Empfehlung: Analysiere die Ursachen für Verzögerungen bei '{top_bottleneck}'.")
    else:
        st.success("Keine auffälligen Engpässe im Prozess erkannt.")

    # Weitere Insights: Fälle mit besonders langer Durchlaufzeit
    st.subheader("Fälle mit langer Durchlaufzeit")
    case_times = df.groupby(case_col)[timestamp_col].agg(['min', 'max'])
    case_times['Durchlaufzeit (min)'] = (pd.to_datetime(case_times['max']) - pd.to_datetime(case_times['min'])).dt.total_seconds() / 60
    long_cases = case_times.sort_values('Durchlaufzeit (min)', ascending=False).head(5)
    st.dataframe(long_cases[['Durchlaufzeit (min)']])
    if not long_cases.empty:
        st.info("Überprüfe die oben stehenden Fälle auf Besonderheiten oder Ausreißer.")