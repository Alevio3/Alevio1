import streamlit as st
import hashlib
from utils import get_user, add_user, password_reset_ui

def login():
    st.title('Alevio Process Mining Login')
    if 'logged_in_user' not in st.session_state:
        register = st.checkbox("Noch keinen Account? Jetzt registrieren!")

        if register:
            st.subheader("Registrieren")
            reg_user = st.text_input("Benutzername", key="reg_user")
            reg_pw = st.text_input("Passwort", type="password", key="reg_pw")
            if st.button("Registrieren"):
                if not reg_user or not reg_pw:
                    st.error("Bitte Benutzername und Passwort eingeben.")
                else:
                    try:
                        add_user(reg_user, reg_pw, role="user")
                        st.success("Registrierung erfolgreich! Sie können sich jetzt einloggen.")
                    except Exception as e:
                        st.error(f"Fehler: {e}")
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