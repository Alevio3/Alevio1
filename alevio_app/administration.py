import streamlit as st
import sqlite3

def administration():
    st.header("Benutzerverwaltung (Admin)")

    # Nur für Admins sichtbar machen
    if st.session_state.get("logged_in_user_role", "user") != "admin":
        st.warning("Zugriff nur für Administratoren.")
        return

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Benutzerliste anzeigen
    st.subheader("Alle Benutzer")
    users = c.execute("SELECT username, role FROM users").fetchall()
    st.table(users)

    # Benutzer anlegen
    st.subheader("Neuen Benutzer anlegen")
    new_user = st.text_input("Benutzername", key="new_user")
    new_pw = st.text_input("Passwort", type="password", key="new_pw")
    new_role = st.selectbox("Rolle", ["user", "admin"], key="new_role")
    if st.button("Benutzer anlegen"):
        if not new_user or not new_pw:
            st.error("Bitte Benutzername und Passwort eingeben.")
        elif any(u[0] == new_user for u in users):
            st.error("Benutzername existiert bereits.")
        else:
            try:
                from utils import add_user
                add_user(new_user, new_pw, role=new_role)
                st.success("Benutzer erfolgreich angelegt!")
                st.rerun()
            except Exception as e:
                st.error(f"Fehler: {e}")

    # Benutzer löschen
    st.subheader("Benutzer löschen")
    del_user = st.selectbox("Benutzer auswählen", [u[0] for u in users if u[0] != "admin"])
    if st.button("Benutzer löschen"):
        c.execute("DELETE FROM users WHERE username=?", (del_user,))
        conn.commit()
        st.success(f"Benutzer {del_user} gelöscht.")
        st.rerun()

    conn.close()