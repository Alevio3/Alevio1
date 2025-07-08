import streamlit as st
import pandas as pd

def bottleneck_analyse():
    st.header('Bottleneck Analyse')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return

    df = st.session_state['df']
    # Spaltenauswahl
    default_case = st.session_state.get('case_col', df.columns[0])
    default_activity = st.session_state.get('activity_col', df.columns[1])
    default_timestamp = st.session_state.get('timestamp_col', df.columns[2])
    case_col = st.selectbox('Fall-ID Spalte', df.columns, key='bottleneck_case_col', index=list(df.columns).index(default_case) if default_case in df.columns else 0)
    activity_col = st.selectbox('Aktivitäten-Spalte', df.columns, key='bottleneck_activity_col', index=list(df.columns).index(default_activity) if default_activity in df.columns else 1)
    timestamp_col = st.selectbox('Zeitstempel-Spalte', df.columns, key='bottleneck_timestamp_col', index=list(df.columns).index(default_timestamp) if default_timestamp in df.columns else 2)
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # Verweildauer je Aktivität berechnen
    df = df.sort_values([case_col, timestamp_col])
    df['next_activity'] = df.groupby(case_col)[activity_col].shift(-1)
    df['next_timestamp'] = df.groupby(case_col)[timestamp_col].shift(-1)
    df['duration'] = (df['next_timestamp'] - df[timestamp_col]).dt.total_seconds() / 3600  # in Stunden

    # Nur Zeilen mit gültiger nächster Aktivität
    df_valid = df.dropna(subset=['next_activity', 'duration'])

    # Analyse: Durchschnittliche Verweildauer je Aktivität
    stats = df_valid.groupby(activity_col)['duration'].agg(['count', 'mean', 'min', 'max']).reset_index()
    stats = stats.rename(columns={
        'count': 'Anzahl Übergänge',
        'mean': 'Ø Verweildauer (h)',
        'min': 'Min (h)',
        'max': 'Max (h)'
    })
    stats = stats.sort_values('Ø Verweildauer (h)', ascending=False).reset_index(drop=True)
    top_stats = stats.head(10)

    st.subheader('Top 10 Bottlenecks (Ø Verweildauer je Aktivität)')
    styled_stats = top_stats.style.bar(
        subset=['Ø Verweildauer (h)'],
        color='#e67e22',
        vmin=0,
        align='mid'
    ).format({'Ø Verweildauer (h)': '{:.2f}', 'Min (h)': '{:.2f}', 'Max (h)': '{:.2f}'})

    st.dataframe(styled_stats, use_container_width=True, height=40*len(top_stats)+40)

    # Rechnungsvorlage für den größten Bottleneck
    if not top_stats.empty:
        bottleneck = top_stats.iloc[0]
        st.markdown("---")
        st.markdown(f"### Größter Bottleneck: **{bottleneck[activity_col]}**")
        st.info(f"Diese Aktivität hat die höchste durchschnittliche Verweildauer mit **{bottleneck['Ø Verweildauer (h)']:.2f} Stunden** pro Übergang.")

        st.markdown("#### Rechnungsvorlage: Potenzielle Einsparung")
        hourly_rate = st.number_input("Stundensatz (€ pro Stunde)", min_value=0.0, value=80.0, step=1.0)
        reduction_percent = st.slider("Angestrebte Reduktion der Verweildauer (%)", 0, 100, 20)
        anzahl_uebergaenge = bottleneck['Anzahl Übergänge']
        zeit_ersparnis_gesamt = bottleneck['Ø Verweildauer (h)'] * (reduction_percent/100) * anzahl_uebergaenge
        geld_ersparnis = zeit_ersparnis_gesamt * hourly_rate

        st.success(
            f"""
            **Wenn Sie die Verweildauer von _{bottleneck[activity_col]}_ um {reduction_percent}% senken:**  
            - Ersparte Zeit gesamt: **{zeit_ersparnis_gesamt:.1f} Stunden**  
            - Monetäre Ersparnis: **{geld_ersparnis:,.2f} €**
            """
        )