"""Simple sqlite cache to reduce repeated LLM calls for identical prompts."""
import sqlite3
import hashlib
import json
from pathlib import Path

DB = Path('.jarvis_cache.db')

def _get_conn():
    conn = sqlite3.connect(str(DB))
    conn.execute('''CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, response TEXT, ts INTEGER)''')
    return conn

def get(prompt_key):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute('SELECT response FROM cache WHERE key=?', (prompt_key,))
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def set(prompt_key, response):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO cache (key, response, ts) VALUES (?,?,strftime("%s","now"))', (prompt_key, json.dumps(response)))
    conn.commit()
    conn.close()


def key_for_messages(messages):
    s = ''.join([m.get('role','')+m.get('content','') for m in messages])
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
