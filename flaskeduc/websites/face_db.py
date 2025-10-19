import sqlite3
import pickle
import os

DB_PATH = "students.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            username TEXT PRIMARY KEY,
            encoding BLOB
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, encoding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM faces WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False
    c.execute("INSERT INTO faces (username, encoding) VALUES (?, ?)", (username, pickle.dumps(encoding)))
    conn.commit()
    conn.close()
    return True

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, encoding FROM faces")
    users = [(row[0], pickle.loads(row[1])) for row in c.fetchall()]
    conn.close()
    return users

# Initialize database on import
create_database()