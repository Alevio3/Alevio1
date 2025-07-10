import streamlit as st
import pandas as pd
from project_utils import get_projects, add_project, save_project_csv, load_project_csv, delete_project

TEAMS = ["Controlling", "Einkauf", "IT", "Vertrieb"]

def project_dashboard():
    st.header("Projektübersicht")
    user_id = st.session_state.get('logged_in_user')
    if not user_id:
        st.info("Bitte zuerst einloggen.")
        return

    option = st.radio(
        "Was möchten Sie tun?",
        ("Neues Projekt anlegen", "Meine Projekte bearbeiten"),
        horizontal=True,
    )

    # 1. Neues Projekt anlegen
    if option == "Neues Projekt anlegen":
        st.subheader("Neues Projekt anlegen")
        uploaded_file = st.file_uploader("CSV Datei hochladen", type=["csv"])
        team = st.selectbox("Team auswählen", TEAMS)
        project_name = st.text_input("Projektname")
        if st.button("Weiter", type="primary"):
            if not uploaded_file or not team or not project_name:
                st.error("Bitte alle Felder ausfüllen und eine Datei hochladen.")
            else:
                df = pd.read_csv(uploaded_file)
                add_project(user_id, project_name, "Bereich", team)
                # Ermittle die ID des zuletzt angelegten Projekts für diesen Nutzer
                projects = get_projects(user_id)
                project_id = projects[-1][0] if projects else None
                if project_id:
                    save_project_csv(project_id, df)
                    st.success(f"Projekt '{project_name}' für Team '{team}' angelegt!")
                    st.dataframe(df.head())
                else:
                    st.error("Projekt konnte nicht gespeichert werden.")

    # 2. Meine Projekte bearbeiten
    elif option == "Meine Projekte bearbeiten":
        st.subheader("Meine Projekte")
        projects = get_projects(user_id)
        if not projects:
            st.info("Noch keine Projekte vorhanden.")
        else:
            df_proj = pd.DataFrame(projects, columns=["ID", "Projektname", "Bereich", "Team", "Erstellt am"])
            selected = st.selectbox("Projekt auswählen", df_proj["Projektname"])
            proj = df_proj[df_proj["Projektname"] == selected].iloc[0]
            if st.button("Details anzeigen"):
                st.markdown(f"### Projektdetails")
                st.write(f"**Name:** {proj['Projektname']}")
                st.write(f"**Team:** {proj['Team']}")
                st.write(f"**Bereich:** {proj['Bereich']}")
                st.write(f"**Erstellt am:** {proj['Erstellt am']}")
                st.info("Hier könnten weitere Details und Aktionen stehen.")
            if st.button("Projekt löschen"):
                delete_project(proj["ID"])
                st.success("Projekt gelöscht!")
                st.experimental_rerun()  # Seite neu laden, damit das gelöschte Projekt verschwindet
            if st.button("Daten anzeigen"):
                df = load_project_csv(proj["ID"])
                if df is not None:
                    st.dataframe(df)
                else:
                    st.info("Für dieses Projekt wurden noch keine Daten hochgeladen.")
