
import sqlite3
from datetime import datetime
DB_PATH = "astro.db"

DDL = '''
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS usage (
  user_id INTEGER PRIMARY KEY,
  window_start TEXT,
  count INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE IF NOT EXISTS logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  command TEXT,
  payload TEXT,
  created_at TEXT
);
'''

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for stmt in DDL.strip().split(';'):
        s = stmt.strip()
        if s:
            cur.execute(s)
    conn.commit(); conn.close()

def ensure_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, created_at) VALUES (?, ?)", (user_id, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_usage(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT window_start, count FROM usage WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def set_usage(user_id: int, window_start: str, count: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO usage (user_id, window_start, count) VALUES (?, ?, ?)", (user_id, window_start, count))
    conn.commit(); conn.close()

def log_event(user_id: int, command: str, payload: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (user_id, command, payload, created_at) VALUES (?, ?, ?, ?)", (user_id, command, payload, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
