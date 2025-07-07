import streamlit as st
import pandas as pd
import plotly.express as px

def kpi_dashboard():
    st.header("KPI Dashboard")

    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        st.stop()

    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    activity_col = st.session_state.get('activity_col', df.columns[1])
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])

    # Zeitspalte als datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # KPIs berechnen
    total_cases = df[case_col].nunique()
    total_activities = df[activity_col].nunique()
    total_events = len(df)
    start_time = df[timestamp_col].min()
    end_time = df[timestamp_col].max()
    throughput_time = (end_time - start_time).total_seconds() / 3600  # in Stunden

    # Durchlaufzeit pro Fall
    case_durations = df.groupby(case_col)[timestamp_col].agg(['min', 'max'])
    case_durations['duration'] = (case_durations['max'] - case_durations['min']).dt.total_seconds() / 3600
    avg_case_duration = case_durations['duration'].mean()
    min_case_duration = case_durations['duration'].min()
    max_case_duration = case_durations['duration'].max()

    # Layout wie in SAC: KPIs als "Tiles"
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Anzahl Fälle", f"{total_cases}")
    col2.metric("Anzahl Aktivitäten", f"{total_activities}")
    col3.metric("Anzahl Events", f"{total_events}")
    col4.metric("Zeitraum", f"{start_time.date()} - {end_time.date()}")

    col5, col6, col7 = st.columns(3)
    col5.metric("Ø Durchlaufzeit (h)", f"{avg_case_duration:.2f}")
    col6.metric("Min. Durchlaufzeit (h)", f"{min_case_duration:.2f}")
    col7.metric("Max. Durchlaufzeit (h)", f"{max_case_duration:.2f}")

    st.markdown("---")

    # Aktivitäten-Häufigkeit als Balkendiagramm
    st.subheader("Aktivitäten-Häufigkeit")
    activity_counts = df[activity_col].value_counts().reset_index()
    activity_counts.columns = [activity_col, "Anzahl"]
    fig1 = px.bar(activity_counts, x=activity_col, y="Anzahl", color="Anzahl", color_continuous_scale="Blues")
    st.plotly_chart(fig1, use_container_width=True)

    # Durchlaufzeiten als Boxplot
    st.subheader("Durchlaufzeiten pro Fall")
    fig2 = px.box(case_durations, y="duration", points="all", labels={"duration": "Durchlaufzeit (h)"})
    st.plotly_chart(fig2, use_container_width=True)

    # Fälle pro Zeit (z.B. pro Woche)
    st.subheader("Fälle pro Woche")
    df_cases = df.groupby(case_col)[timestamp_col].min().reset_index()
    df_cases['Woche'] = df_cases[timestamp_col].dt.to_period('W').astype(str)
    cases_per_week = df_cases.groupby('Woche')[case_col].count().reset_index()
    fig3 = px.line(cases_per_week, x="Woche", y=case_col, markers=True, labels={case_col: "Fälle"})
    st.plotly_chart(fig3, use_container_width=True)

    # Optional: Top 5 Varianten
    st.subheader("Top 5 Prozessvarianten")
    variants = df.groupby(case_col)[activity_col].apply(list)
    variants_count = variants.value_counts().reset_index()
    variants_count.columns = ['Variante', 'Anzahl']

    for i, row in variants_count.head(5).iterrows():
        st.markdown(
            f"""
            <div style="margin-bottom: 1em;">
                <b>Variante {i+1}</b> (Anzahl: {row['Anzahl']}):<br>
                {" ".join([f'<span style="background-color:#e0e0e0;border-radius:8px;padding:4px 8px;margin:2px;display:inline-block;">{act}</span>' for act in row['Variante']])}
            </div>
            """,
            unsafe_allow_html=True
        )