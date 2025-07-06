import streamlit as st

def login():
    st.title("Log-In")

    # Login-Status in Session State speichern
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        if st.button("Login"):
            # Hier könntest du echte Authentifizierung einbauen
            if username == "admin" and password == "pass":  # Beispiel
                st.session_state.logged_in = True
                st.success("Login erfolgreich!")
            else:
                st.error("Falscher Benutzername oder Passwort.")
    else:
        st.success("Login erfolgreich!")
        st.header("Was möchtest du tun?")
        auswahl = st.radio(
            "Bitte wählen:",
            ("Neues Projekt anlegen", "Bestehendes Projekt bearbeiten")
        )
        if auswahl == "Neues Projekt anlegen":
            st.info("Hier könntest du die Seite zum Anlegen eines neuen Projekts aufrufen.")
            # z.B. pages.neuer_prozess()
        elif auswahl == "Bestehendes Projekt bearbeiten":
            st.info("Hier könntest du die Seite zum Bearbeiten eines Projekts aufrufen.")
            # z.B. pages.control_center()