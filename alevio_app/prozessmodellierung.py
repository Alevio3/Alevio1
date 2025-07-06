import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def alpha_miner(df, case_col, activity_col, timestamp_col):
    # Sortiere nach Case und Zeit
    df = df.sort_values([case_col, timestamp_col])
    # Extrahiere alle einzigartigen Aktivitäten
    activities = df[activity_col].unique()
    # Erzeuge Kanten: (A, B) wenn B direkt nach A in einem Case kommt
    edges = set()
    for case_id, group in df.groupby(case_col):
        acts = group[activity_col].tolist()
        for i in range(len(acts)-1):
            edges.add((acts[i], acts[i+1]))
    return activities, edges

def prozessmodellierung(df, case_col, activity_col, timestamp_col):
    st.title("Prozessmodellierung (Alpha Miner)")
    activities, edges = alpha_miner(df, case_col, activity_col, timestamp_col)
    G = nx.DiGraph()
    G.add_nodes_from(activities)
    G.add_edges_from(edges)

    # Visualisierung
    plt.figure(figsize=(8,5))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, arrowstyle='-|>', arrowsize=20)
    st.pyplot(plt)

    st.write("Aktivitäten:", activities)
    st.write("Kanten:", list(edges))