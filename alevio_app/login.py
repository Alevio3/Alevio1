import streamlit as st
import hashlib
import os
import sqlite3

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), "users.db")
    return sqlite3.connect(db_path)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, role="user"):
    conn = get_db()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, salt TEXT, role TEXT)")
    try:
        c.execute("INSERT INTO users (username, password, salt, role) VALUES (?, ?, '', ?)",
                  (username, hash_password(password), role))
        conn.commit()
    except sqlite3.IntegrityError:
        raise Exception("Benutzername existiert bereits.")
    conn.close()

def password_reset_ui():
    st.subheader("Passwort zurücksetzen")
    username = st.text_input("Benutzername")
    new_password = st.text_input("Neues Passwort", type="password")
    new_password2 = st.text_input("Neues Passwort wiederholen", type="password")
    if st.button("Passwort zurücksetzen"):
        if not username or not new_password:
            st.error("Bitte alle Felder ausfüllen.")
            return
        if new_password != new_password2:
            st.error("Passwörter stimmen nicht überein.")
            return
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user:
            c.execute("UPDATE users SET password = ? WHERE username = ?",
                      (hash_password(new_password), username))
            conn.commit()
            st.success("Passwort erfolgreich zurückgesetzt! Sie können sich jetzt einloggen.")
        else:
            st.error("Benutzername existiert nicht.")
        conn.close()

def register():
    st.subheader("Registrieren")
    reg_user = st.text_input("Benutzername", key="reg_user")
    reg_pw = st.text_input("Passwort", type="password", key="reg_pw")
    if st.button("Registrieren"):
        st.session_state['show_register'] = True

    if st.session_state.get('show_register'):
        register()

def login():
    st.title('Alevio Process Mining Login')
    if 'logged_in_user' not in st.session_state:
        register = st.checkbox("Noch keinen Account? Jetzt registrieren!")

        if register:
            st.subheader("Registrieren")
            reg_user = st.text_input("Benutzername", key="reg_user")
            reg_pw = st.text_input("Passwort", type="password", key="reg_pw")
            if st.button("Registrieren"):
                st.session_state['show_register'] = True

            if st.session_state.get('show_register'):
                register()
        else:
            with st.form('login_form'):
                username = st.text_input('Benutzername')
                password = st.text_input('Passwort', type='password')
                submit = st.form_submit_button('Login')
                if submit:
                    user = get_user(username)
                    if user:
                        db_username, db_pw, db_salt, db_role = user
                        hashed_input = hashlib.pbkdf2_hmac('sha256', password.encode(), db_salt.encode(), 100000).hex()
                        if db_pw == hashed_input:
                            st.session_state['logged_in_user'] = username
                            st.session_state['logged_in_user_role'] = db_role
                            st.success(f'Willkommen, {username}!')
                            st.rerun()
                        else:
                            st.error('Falsches Passwort. Bitte erneut versuchen.')
                    else:
                        st.error('Benutzername existiert nicht.')
            if st.button('Passwort vergessen?'):
                st.session_state['show_pw_reset'] = True
                st.rerun()
            if st.session_state.get('show_pw_reset'):
                password_reset_ui()
            st.stop()
    else:
        st.success(f"Willkommen, {st.session_state['logged_in_user']}! Sie sind eingeloggt.")
        st.markdown("Wählen Sie im Menü links eine Funktion aus oder klicken Sie auf **Weiter**.")