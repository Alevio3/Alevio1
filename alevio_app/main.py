import sys
import os
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from login import login
from upload_csv import upload_csv
from Prozessvisualisierung import prozessvisualisierung
from kpi_dashboard import kpi_dashboard
from bottleneck_analyse import bottleneck_analyse
from action_engine import action_engine
from simulation import simulation
from administration import administration
from project_dashboard import project_dashboard

from project_utils import get_projects, add_project, save_project_csv, load_project_csv

st.set_page_config(page_title="Alevio Process Mining", layout="wide")

# Logo oben in die Sidebar einfügen
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo.png")
    st.image(logo_path, width=220)
    st.markdown("---")

# --- Projekt-/Benutzerverwaltung (NEU) ---
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            projektname TEXT,
            bereich TEXT,
            team TEXT,
            erstellt_am TEXT,
            FOREIGN KEY(user_id) REFERENCES users(username)
        )
    """)
    return conn

def add_project(user_id, projektname, bereich, team):
    conn = get_db()
    c = conn.cursor()
    erstellt_am = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO projects (user_id, projektname, bereich, team, erstellt_am) VALUES (?, ?, ?, ?, ?)",
        (user_id, projektname, bereich, team, erstellt_am)
    )
    conn.commit()
    conn.close()

def get_projects(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, projektname, bereich, team, erstellt_am FROM projects WHERE user_id = ?", (user_id,))
    projects = c.fetchall()
    conn.close()
    return projects

def save_project_csv(project_id, df):
    os.makedirs("project_data", exist_ok=True)
    csv_path = f"project_data/project_{project_id}.csv"
    df.to_csv(csv_path, index=False)
    return csv_path

def load_project_csv(project_id):
    csv_path = f"project_data/project_{project_id}.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

def project_form(user_id):
    st.subheader("Neues Projekt anlegen")
    projektname = st.text_input("Projektname")
    bereich = st.text_input("Bereich")
    team = st.text_input("Team")
    if st.button("Projekt speichern"):
        if not projektname or not bereich or not team:
            st.error("Bitte alle Felder ausfüllen.")
            return
        add_project(user_id, projektname, bereich, team)
        st.success("Projekt gespeichert!")
        st.experimental_rerun()

def project_upload(project_id):
    st.subheader("CSV-Daten für dieses Projekt hochladen")
    uploaded_file = st.file_uploader("CSV-Datei auswählen", type=["csv"], key=f"csv_{project_id}")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        save_project_csv(project_id, df)
        st.success("Datei gespeichert!")
        st.dataframe(df.head())

def project_data_view(project_id):
    st.subheader("Projekt-Daten")
    df = load_project_csv(project_id)
    if df is not None:
        st.dataframe(df)
    else:
        st.info("Für dieses Projekt wurden noch keine Daten hochgeladen.")

def my_projects_ui(user_id):
    st.sidebar.markdown("---")
    st.sidebar.subheader("Meine Projekte")
    projects = get_projects(user_id)
    if not projects:
        st.info("Keine Projekte vorhanden.")
        if st.button("Neues Projekt anlegen"):
            st.session_state['show_project_form'] = True
        if st.session_state.get('show_project_form'):
            project_form(user_id)
    else:
        df_proj = pd.DataFrame(projects, columns=["ID", "Projektname", "Bereich", "Team", "Erstellt am"])
        st.table(df_proj[["Projektname", "Bereich", "Team", "Erstellt am"]])
        selected = st.selectbox("Projekt auswählen", df_proj["Projektname"])
        project_id = int(df_proj[df_proj["Projektname"] == selected]["ID"].values[0])
        st.markdown("### Aktionen für dieses Projekt")
        if st.button("CSV hochladen", key=f"upload_{project_id}"):
            st.session_state['show_upload'] = project_id
        if st.button("Daten anzeigen", key=f"data_{project_id}"):
            st.session_state['show_data'] = project_id
        if st.session_state.get('show_upload') == project_id:
            project_upload(project_id)
        if st.session_state.get('show_data') == project_id:
            project_data_view(project_id)

# --- Seitenliste inkl. Meine Projekte ---
PAGES = [
    "Daten hochladen",
    "Prozessvisualisierung",
    "KPI Dashboard",
    "Bottleneck Analyse",
    "Handlungsempfehlungen",
    "Simulation",
    "Administration",
    "Meine Projekte",
    "Projektübersicht"  # <-- NEU
]

def main():
    if 'page_idx' not in st.session_state:
        st.session_state['page_idx'] = 0

    st.session_state['PAGES'] = PAGES

    # LOGOUT-BUTTON (optional)
    if 'logged_in_user' in st.session_state:
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", type="primary"):
            del st.session_state['logged_in_user']
            st.rerun()

    # LOGIN
    if 'logged_in_user' not in st.session_state:
        st.sidebar.title("Navigation")
        st.sidebar.info("Bitte zuerst einloggen.")
        login()
        return

    # Seiten-Navigation per Index
    page_idx = st.session_state['page_idx']
    nav = PAGES[page_idx]
    st.sidebar.title("Navigation")
    st.sidebar.write(f"Aktuelle Seite: **{nav}**")

    selected = st.sidebar.radio("Navigation", PAGES, index=st.session_state['page_idx'])
    if selected != PAGES[st.session_state['page_idx']]:
        st.session_state['page_idx'] = PAGES.index(selected)
        st.rerun()

    # Seiteninhalt anzeigen
    if nav == 'Daten hochladen':
        upload_csv()
    elif nav == 'Prozessvisualisierung':
        prozessvisualisierung()
    elif nav == 'KPI Dashboard':
        kpi_dashboard()
    elif nav == 'Bottleneck Analyse':
        bottleneck_analyse()
    elif nav == 'Handlungsempfehlungen':
        action_engine()
    elif nav == 'Simulation':
        simulation()
    elif nav == 'Administration':
        administration()
    elif nav == 'Meine Projekte':
        user_id = st.session_state.get('logged_in_user')
        if user_id:
            my_projects_ui(user_id)
        else:
            st.info("Bitte zuerst einloggen.")
    elif nav == "Projektübersicht":
        project_dashboard()

    # Weiter/Zurück Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück", disabled=page_idx == 0):
            st.session_state['page_idx'] = max(0, page_idx - 1)
            st.rerun()
    with col2:
        if st.button("Weiter", key="weiter_main", disabled=page_idx == len(PAGES) - 1):
            st.session_state['page_idx'] = min(len(PAGES) - 1, page_idx + 1)
            st.rerun()

if __name__ == "__main__":
    main()
