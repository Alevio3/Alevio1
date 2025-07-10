# filepath: /Users/furbware/Documents/GitHub/Alevio1/alevio_app/project_utils.py
import sqlite3
import os
import pandas as pd
from datetime import datetime

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

def delete_project(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    # Optional: CSV-Datei löschen
    csv_path = f"project_data/project_{project_id}.csv"
    if os.path.exists(csv_path):
        os.remove(csv_path)