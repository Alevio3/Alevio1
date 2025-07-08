import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import graphviz

def prozessvisualisierung():
    st.header('Prozessvisualisierung')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        return

    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    activity_col = st.session_state.get('activity_col', df.columns[1])
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])

    st.dataframe(df[[case_col, activity_col, timestamp_col]].head(20))

    vis_option = st.selectbox(
        "Welche Visualisierung möchten Sie sehen?",
        ["DFG-Graph", "Aktivitäts-Häufigkeit", "Swimlane-Chart", "Prozessflussdiagramm", "Varianten-Graph", "Gantt-Chart"]
    )

    if vis_option == "DFG-Graph":
        st.subheader("Directly-Follows-Graph (DFG)")
        try:
            import pm4py
            from pm4py.algo.discovery.dfg import algorithm as dfg_factory
            from pm4py.visualization.dfg import visualizer as dfg_vis_factory

            df_pm = df.rename(columns={
                case_col: "case:concept:name",
                activity_col: "concept:name",
                timestamp_col: "time:timestamp"
            })
            df_pm["time:timestamp"] = pd.to_datetime(df_pm["time:timestamp"])
            dfg = dfg_factory.apply(df_pm)
            gviz = dfg_vis_factory.apply(dfg, log=df_pm)
            st.graphviz_chart(gviz.source)
        except Exception as e:
            st.error(f"Fehler beim Erstellen des DFG-Graphen: {e}")

    elif vis_option == "Aktivitäts-Häufigkeit":
        st.subheader("Häufigkeit der Aktivitäten")
        activity_counts = df[activity_col].value_counts()
        fig, ax = plt.subplots()
        activity_counts.plot(kind='bar', ax=ax, color="#3143b2")
        ax.set_xlabel("Aktivität")
        ax.set_ylabel("Anzahl")
        st.pyplot(fig)

    elif vis_option == "Swimlane-Chart":
        st.subheader("Swimlane-Chart")
        try:
            df_sorted = df.sort_values([case_col, timestamp_col])
            df_sorted['order'] = df_sorted.groupby(case_col).cumcount()
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
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Swimlane-Charts: {e}")

    elif vis_option == "Prozessflussdiagramm":
        st.subheader("Prozessflussdiagramm")
        # Kanten berechnen
        df_sorted = df.sort_values([case_col, timestamp_col])
        df_sorted['next_activity'] = df_sorted.groupby(case_col)[activity_col].shift(-1)
        edges = df_sorted.dropna(subset=['next_activity']).groupby([activity_col, 'next_activity']).size().to_dict()
        nodes = set()
        for (src, tgt), weight in edges.items():
            nodes.add(src)
            nodes.add(tgt)
        dot = graphviz.Digraph()
        for node in nodes:
            dot.node(node, node, shape="box", style="filled", fillcolor="#e2e6f3", fontname="Inter", fontsize="14")
        for (src, tgt), weight in edges.items():
            dot.edge(src, tgt, label=str(weight), color="#3143b2", fontname="Inter", fontsize="12")
        st.graphviz_chart(dot)
        # Download als PNG
        png_bytes = dot.pipe(format='png')
        st.download_button(
            label="Prozessflussdiagramm als PNG herunterladen",
            data=png_bytes,
            file_name="prozessflussdiagramm.png",
            mime="image/png"
        )

    elif vis_option == "Varianten-Graph":
        st.subheader("Interaktive Varianten-Analyse")
        variants = df.groupby(case_col)[activity_col].apply(list)
        variants_count = variants.value_counts().reset_index().rename(columns={0: 'count', activity_col: 'variant'})
        variants_count['variant_str'] = variants_count['variant'].apply(lambda x: ' → '.join(x))
        top_n = 5
        st.write(f"Top {top_n} Varianten:")
        st.table(variants_count[['variant_str', 'count']].head(top_n).rename(columns={'variant_str': 'Variante', 'count': 'Anzahl'}))

        variant_options = variants_count['variant_str'].tolist()[:top_n]
        if variant_options:
            selected_variant = st.selectbox("Variante auswählen für Detail-Graph", variant_options)
            selected_variant_list = selected_variant.split(' → ')
            selected_cases = variants[variants.apply(lambda x: x == selected_variant_list)].index
            st.write(f"Anzahl Fälle mit dieser Variante: {len(selected_cases)}")
            st.write("Fälle:", list(selected_cases))
        else:
            st.info("Keine Varianten gefunden.")

    elif vis_option == "Gantt-Chart":
        st.subheader("Gantt-Chart")
        try:
            df_gantt = df.copy()
            df_gantt[timestamp_col] = pd.to_datetime(df_gantt[timestamp_col])
            df_gantt['end_time'] = df_gantt.groupby(case_col)[timestamp_col].shift(-1)
            df_gantt = df_gantt.dropna(subset=['end_time'])
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
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Gantt-Charts: {e}")