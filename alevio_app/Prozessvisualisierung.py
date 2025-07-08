import streamlit as st
import pandas as pd
import plotly.express as px
import graphviz
import io

def prozessvisualisierung():
    st.header('Prozessvisualisierung')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return

    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    default_activity = "Aktivität" if "Aktivität" in df.columns else df.columns[1]
    activity_col = st.session_state.get('activity_col', default_activity)
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])

    if st.checkbox("CSV-Daten anzeigen"):
        st.dataframe(df[[case_col, activity_col, timestamp_col]].head(20))

    vis_option = st.selectbox(
        "Welche Visualisierung möchten Sie sehen?",
        ["Aktivitäts-Häufigkeit", "Swimlane-Chart", "Prozessflussdiagramm", "Varianten-Graph", "Gantt-Chart"]
    )

    max_elements = st.slider("Wie viele Einträge anzeigen?", min_value=3, max_value=10, value=5)

    if vis_option == "Aktivitäts-Häufigkeit":
        st.subheader("Häufigkeit der Aktivitäten")
        activity_counts = df[activity_col].value_counts().head(max_elements)
        st.bar_chart(activity_counts)
        st.caption(f"Die {max_elements} häufigsten Aktivitäten im Prozess.")
        csv = activity_counts.to_csv().encode('utf-8')
        st.download_button("Aktivitäten als CSV herunterladen", csv, "aktivitaeten.csv", "text/csv")

    elif vis_option == "Swimlane-Chart":
        st.subheader(f"Swimlane-Chart (Top {max_elements} Fälle)")
        top_cases = df[case_col].value_counts().head(max_elements).index
        df_swim = df[df[case_col].isin(top_cases)]
        try:
            df_sorted = df_swim.sort_values([case_col, timestamp_col])
            fig = px.timeline(
                df_sorted,
                x_start=timestamp_col,
                x_end=df_sorted.groupby(case_col)[timestamp_col].shift(-1),
                y=case_col,
                color=activity_col,
                labels={case_col: "Fall", activity_col: "Aktivität"}
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Nur die {max_elements} häufigsten Fälle werden angezeigt.")
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Swimlane-Charts: {e}")

    elif vis_option == "Prozessflussdiagramm":
        st.subheader("Prozessflussdiagramm")
        df_sorted = df.sort_values([case_col, timestamp_col])
        df_sorted['next_activity'] = df_sorted.groupby(case_col)[activity_col].shift(-1)
        edges = df_sorted.dropna(subset=['next_activity']).groupby([activity_col, 'next_activity']).size().sort_values(ascending=False)
        edges = edges.head(max_elements).to_dict()
        nodes = set()
        for (src, tgt), weight in edges.items():
            nodes.add(src)
            nodes.add(tgt)
        dot = graphviz.Digraph()
        for node in nodes:
            dot.node(node, node, shape="box", style="filled", fillcolor="#e2e6f3")
        for (src, tgt), weight in edges.items():
            dot.edge(src, tgt, label=str(weight), color="#3143b2")
        st.graphviz_chart(dot)
        st.caption(f"Nur die {max_elements} häufigsten Übergänge werden angezeigt.")

    elif vis_option == "Varianten-Graph":
        st.subheader(f"Top {max_elements} Prozessvarianten")
        variants = df.groupby(case_col)[activity_col].apply(list)
        variants_count = variants.value_counts().reset_index()
        variants_count.columns = ['Variante', 'Anzahl']
        for i, row in variants_count.head(max_elements).iterrows():
            st.markdown(
                f"<b>Variante {i+1}</b> (Anzahl: {row['Anzahl']}):<br>"
                + " ".join([f'<span style=\"background:#e0e0e0;border-radius:8px;padding:4px 8px;margin:2px;display:inline-block;\">{act}</span>' for act in row['Variante']]),
                unsafe_allow_html=True
            )
        output = io.BytesIO()
        variants_count.head(max_elements).to_excel(output, index=False)
        st.download_button(
            label="Varianten als Excel herunterladen",
            data=output.getvalue(),
            file_name="varianten.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif vis_option == "Gantt-Chart":
        st.subheader("Gantt-Chart")
        try:
            df_gantt = df.copy()
            df_gantt[timestamp_col] = pd.to_datetime(df_gantt[timestamp_col])
            df_gantt['end_time'] = df_gantt.groupby(case_col)[timestamp_col].shift(-1)
            df_gantt = df_gantt.dropna(subset=['end_time'])
            # Nur Top max_elements Fälle anzeigen
            top_cases = df_gantt[case_col].value_counts().head(max_elements).index
            df_gantt = df_gantt[df_gantt[case_col].isin(top_cases)]
            fig = px.timeline(
                df_gantt,
                x_start=timestamp_col,
                x_end='end_time',
                y=case_col,
                color=activity_col,
                labels={case_col: "Fall", activity_col: "Aktivität"}
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Nur die {max_elements} häufigsten Fälle werden angezeigt.")
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Gantt-Charts: {e}")