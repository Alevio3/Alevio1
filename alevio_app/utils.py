import sqlite3
import streamlit as st
import hashlib

def get_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username, password, salt, role FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password, role='user'):
    salt = hashlib.sha256(username.encode()).hexdigest()
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, salt, role) VALUES (?, ?, ?, ?)', (username, hashed_pw, salt, role))
    conn.commit()

def password_reset_ui():
    st.subheader("Passwort zurücksetzen")
    username = st.text_input("Benutzername für Passwort-Reset")
    new_pw = st.text_input("Neues Passwort", type="password")
    if st.button("Passwort zurücksetzen"):
        salt = hashlib.sha256(username.encode()).hexdigest()
        hashed_pw = hashlib.pbkdf2_hmac('sha256', new_pw.encode(), salt.encode(), 100000).hex()
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE users SET password=?, salt=? WHERE username=?', (hashed_pw, salt, username))
        conn.commit()
        conn.close()
        st.success("Passwort wurde zurückgesetzt.")

