import streamlit as st
import pandas as pd

def simulation():
    st.markdown(
        """
        <style>
        .kpi-card {
            background: #f5f7fa;
            border-radius: 12px;
            padding: 1.5em 1em 1em 1em;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 8px rgba(44,62,80,0.04);
            text-align: center;
        }
        .kpi-title {
            color: #3143b2;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 0.2em;
        }
        .kpi-value {
            font-size: 2.2em;
            font-weight: 700;
            color: #222;
        }
        .money-card {
            background: #eafaf1;
            border-radius: 12px;
            padding: 1.2em 1em 1em 1em;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 8px rgba(39,174,96,0.07);
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.header(' Simulation')
    st.caption('Simulieren Sie Prozessverbesserungen durch Anpassung von Aktivitäten und Ressourcen.')

    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return

    df_orig = st.session_state['df'].copy()
    default_case = "Case ID" if "Case ID" in df_orig.columns else df_orig.columns[0]
    default_activity = "Activity" if "Activity" in df_orig.columns else df_orig.columns[1]
    default_timestamp = "Start Timestamp" if "Start Timestamp" in df_orig.columns else df_orig.columns[2]

    with st.expander("Prozessdaten Vorschau", expanded=False):
        st.dataframe(df_orig.head(20), use_container_width=True)

    st.markdown("### Einstellungen")
    col1, col2, col3 = st.columns(3)
    with col1:
        case_col = st.selectbox('Fall-ID Spalte', df_orig.columns, key='sim_case_col', index=list(df_orig.columns).index(default_case) if default_case in df_orig.columns else 0)
    with col2:
        activity_col = st.selectbox('Aktivitäten-Spalte', df_orig.columns, key='sim_activity_col', index=list(df_orig.columns).index(default_activity) if default_activity in df_orig.columns else 1)
    with col3:
        timestamp_col = st.selectbox('Zeitstempel-Spalte', df_orig.columns, key='sim_timestamp_col', index=list(df_orig.columns).index(default_timestamp) if default_timestamp in df_orig.columns else 2)
    df_orig[timestamp_col] = pd.to_datetime(df_orig[timestamp_col])

    st.markdown("### Simulationsparameter")
    sim_mode = st.radio("Bearbeitungszeit reduzieren für...", ["Nur eine Aktivität", "Alle Aktivitäten"], horizontal=True)
    if sim_mode == "Nur eine Aktivität":
        activities = df_orig[activity_col].unique()
        selected_act = st.selectbox("Aktivität wählen", activities)
    reduction_type = st.radio("Reduktionsart wählen", ["Prozentual (%)", "Absolut (Minuten)"], horizontal=True)
    if reduction_type == "Prozentual (%)":
        reduction = st.slider("Bearbeitungszeit reduzieren um (%)", 0, 100, 20)
    else:
        reduction = st.number_input("Bearbeitungszeit reduzieren um (Minuten)", min_value=0.0, value=5.0, step=0.5)

    # --- Lead Time vorher ---
    df_before = df_orig.copy()
    df_before = df_before.sort_values([case_col, timestamp_col])
    prozess_dauern_ist = df_before.groupby(case_col).agg({timestamp_col: ['min', 'max']})
    prozess_dauern_ist['Lead Time'] = (prozess_dauern_ist[(timestamp_col, 'max')] - prozess_dauern_ist[(timestamp_col, 'min')]).dt.total_seconds() / 86400
    avg_ist = prozess_dauern_ist['Lead Time'].mean()

    # --- Simulation mit kaskadierender Zeitverschiebung ---
    df_sim = df_orig.copy()
    df_sim = df_sim.sort_values([case_col, timestamp_col])
    for case_id, group in df_sim.groupby(case_col):
        group = group.sort_values(timestamp_col).copy()
        for i, row in enumerate(group.itertuples()):
            if sim_mode == "Nur eine Aktivität":
                match = getattr(row, activity_col) == selected_act
            else:
                match = True
            if match and i < len(group) - 1:
                orig_delta = group.iloc[i+1][timestamp_col] - group.iloc[i][timestamp_col]
                if reduction_type == "Prozentual (%)":
                    new_delta = orig_delta * (1 - reduction/100)
                else:
                    new_delta = orig_delta - pd.to_timedelta(reduction, unit='m')
                    if new_delta < pd.Timedelta(0):
                        new_delta = pd.Timedelta(0)
                diff = orig_delta - new_delta
                group.loc[group.index[i+1]:, timestamp_col] = group.loc[group.index[i+1]:, timestamp_col] - diff
        df_sim.loc[group.index, timestamp_col] = group[timestamp_col]

    # Neue Lead Times berechnen
    prozess_dauern_sim = df_sim.groupby(case_col).agg({timestamp_col: ['min', 'max']})
    prozess_dauern_sim['Simulierte Lead Time'] = (prozess_dauern_sim[(timestamp_col, 'max')] - prozess_dauern_sim[(timestamp_col, 'min')]).dt.total_seconds() / 86400
    avg_sim = prozess_dauern_sim['Simulierte Lead Time'].mean()

    st.markdown("### Ergebnisse")
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Durchschnittliche Lead Time vorher</div>
            <div class="kpi-value">{avg_ist:.2f} Tage</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Durchschnittliche Lead Time nachher</div>
            <div class="kpi-value">{avg_sim:.2f} Tage</div>
        </div>
        """, unsafe_allow_html=True)

    # Monetäre Auswertung
    st.markdown("### Monetäre Auswertung")
    hourly_rate = st.number_input("Stundensatz (€ pro Stunde)", min_value=0.0, value=80.0, step=1.0)
    time_saved_days = avg_ist - avg_sim
    time_saved_hours = time_saved_days * 24
    total_cases = df_orig[case_col].nunique()
    total_hours_saved = time_saved_hours * total_cases
    total_savings = total_hours_saved * hourly_rate

    st.markdown(f"""
    <div class="money-card">
        <span class="kpi-title">Ersparte Zeit pro Fall</span>
        <div class="kpi-value">{time_saved_hours:.2f} h</div>
        <span class="kpi-title">Gesamtersparnis</span>
        <div class="kpi-value">{total_savings:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    if avg_sim < avg_ist:
        st.success('Die Simulation zeigt eine Reduzierung der durchschnittlichen Durchlaufzeit!')
    else:
        st.warning('Die Simulation zeigt keine Verbesserung der Durchlaufzeit.')
