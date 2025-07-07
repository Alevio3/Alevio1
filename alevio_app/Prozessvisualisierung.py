import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io

def prozessvisualisierung():
    st.header('Prozessvisualisierung')
    if 'df' not in st.session_state:
        st.warning('Bitte laden Sie zuerst eine CSV-Datei hoch.')
        st.stop()
    df = st.session_state['df']
    case_col = st.session_state.get('case_col', df.columns[0])
    activity_col = st.session_state.get('activity_col', df.columns[1])
    timestamp_col = st.session_state.get('timestamp_col', df.columns[2])
    st.dataframe(df[[case_col, activity_col, timestamp_col]].head(20))
    vis_option = st.selectbox(
        "Welche Visualisierung möchten Sie sehen?",
        ["DFG-Graph", "Aktivitäts-Häufigkeit", "Swimlane-Chart", "Prozessflussdiagramm", "Varianten-Graph", "Gantt-Chart"]
    )

    # 1. DFG-Graph (Directly-Follows-Graph mit pm4py)
    if vis_option == "DFG-Graph":
        st.subheader("Prozessgraph (Directly-Follows-Graph)")
        try:
            import pm4py
            from pm4py.visualization.dfg import factory as dfg_vis_factory
            from pm4py.algo.discovery.dfg import factory as dfg_factory

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

    # 2. Aktivitäts-Häufigkeit (Balkendiagramm)
    if vis_option == "Aktivitäts-Häufigkeit":
        st.subheader("Häufigkeit der Aktivitäten")
        activity_counts = df[activity_col].value_counts()
        fig, ax = plt.subplots()
        activity_counts.plot(kind='bar', ax=ax)
        ax.set_xlabel("Aktivität")
        ax.set_ylabel("Anzahl")
        st.pyplot(fig)

    # 3. Swimlane-Chart (Plotly)
    if vis_option == "Swimlane-Chart":
        variants = df.groupby(case_col)[activity_col].apply(list)
        variants_count = variants.value_counts().reset_index().rename(columns={0: 'count', activity_col: 'variant'})
        variants_count['variant_str'] = variants_count['variant'].apply(lambda x: ' → '.join(x))
        top_n = 5
        variant_options = variants_count['variant_str'].tolist()[:top_n]
        if variant_options:
            selected_variant = st.selectbox("Variante auswählen für Swimlane-Ansicht", variant_options)
            selected_variant_list = selected_variant.split(' → ')
            swimlane_df = df[df[case_col].isin(
                variants[variants.apply(lambda x: x == selected_variant_list)].index
            )].copy()
            swimlane_df = swimlane_df.sort_values([case_col, timestamp_col])
            swimlane_df['activity_order'] = swimlane_df.groupby(case_col).cumcount()
            fig = px.timeline(
                swimlane_df,
                x_start=timestamp_col,
                x_end=swimlane_df.groupby(case_col)[timestamp_col].shift(-1),
                y=case_col,
                color=activity_col,
                title="Swimlane-Ansicht für ausgewählte Variante",
                labels={case_col: "Fall", activity_col: "Aktivität"}
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=30))
            st.plotly_chart(fig, use_container_width=True)
            buf = io.BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            st.download_button(
                label="Swimlane-Chart als PNG herunterladen",
                data=buf,
                file_name="swimlane_chart.png",
                mime="image/png"
            )
        else:
            st.info("Keine Varianten gefunden.")

    # 4. Prozessflussdiagramm (vereinfachtes Sankey-Diagramm)
    if vis_option == "Prozessflussdiagramm":
        st.subheader("Prozessflussdiagramm (Sankey)")
        try:
            import plotly.graph_objects as go
            # Kanten berechnen
            edges = df.groupby([activity_col]).size().reset_index(name='count')
            # Für ein echtes Sankey: Paare von Aktivitäten (Directly-Follows)
            df_sorted = df.sort_values([case_col, timestamp_col])
            df_sorted['next_activity'] = df_sorted.groupby(case_col)[activity_col].shift(-1)
            dfg = df_sorted.dropna(subset=['next_activity']).groupby([activity_col, 'next_activity']).size().reset_index(name='count')
            all_acts = list(pd.unique(dfg[[activity_col, 'next_activity']].values.ravel('K')))
            act_idx = {act: i for i, act in enumerate(all_acts)}
            fig = go.Figure(go.Sankey(
                node=dict(label=all_acts),
                link=dict(
                    source=[act_idx[a] for a in dfg[activity_col]],
                    target=[act_idx[a] for a in dfg['next_activity']],
                    value=dfg['count']
                )
            ))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Prozessflussdiagramms: {e}")

    # 5. Varianten-Graph (Top 5 Varianten als Graph)
    if vis_option == "Varianten-Graph":
        st.subheader("Varianten-Graph (Top 5)")
        variants = df.groupby(case_col)[activity_col].apply(list)
        variants_count = variants.value_counts().reset_index().rename(columns={0: 'count', activity_col: 'variant'})
        top_n = 5
        for i, row in variants_count.head(top_n).iterrows():
            st.markdown(f"**Variante {i+1}** (Anzahl: {row['count']}):")
            st.markdown(" → ".join(row['variant']))

    # 6. Gantt-Chart (Plotly)
    if vis_option == "Gantt-Chart":
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
                title="Gantt-Chart",
                labels={case_col: "Fall", activity_col: "Aktivität"}
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=30))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Gantt-Charts: {e}")