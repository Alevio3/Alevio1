import sqlite3

# Verbindung zur Datenbank (erstellt sie, falls nicht vorhanden)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Tabelle 'users' anlegen
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Tabelle 'users' wurde erfolgreich angelegt.")