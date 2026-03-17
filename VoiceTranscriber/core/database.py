import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path


class Database:
    """SQLite database for transcription archive and settings."""

    def __init__(self):
        cache_dir = Path.home() / ".cache" / "voice_transcriber"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / "transcriber.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    raw_text TEXT,
                    provider TEXT,
                    model TEXT,
                    timestamp TEXT NOT NULL,
                    duration_sec REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    api_key TEXT,
                    base_url TEXT,
                    model TEXT,
                    prompt TEXT,
                    is_active INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def save_transcription(self, text, raw_text=None, provider=None, model=None, duration_sec=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO archive (text, raw_text, provider, model, timestamp, duration_sec) VALUES (?, ?, ?, ?, ?, ?)",
                (text, raw_text, provider, model, datetime.now().isoformat(), duration_sec),
            )
            # Keep only last 25
            conn.execute("""
                DELETE FROM archive WHERE id NOT IN (
                    SELECT id FROM archive ORDER BY id DESC LIMIT 25
                )
            """)
            conn.commit()

    def get_archive(self, limit=25):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM archive ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def save_provider(self, name, provider_type, api_key="", base_url="", model="", prompt=""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO providers (name, provider_type, api_key, base_url, model, prompt) VALUES (?, ?, ?, ?, ?, ?)",
                (name, provider_type, api_key, base_url, model, prompt),
            )
            conn.commit()

    def update_provider(self, provider_id, **kwargs):
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [provider_id]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE providers SET {sets} WHERE id = ?", vals)
            conn.commit()

    def delete_provider(self, provider_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
            conn.commit()

    def get_providers(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM providers ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def set_active_provider(self, provider_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE providers SET is_active = 0")
            conn.execute("UPDATE providers SET is_active = 1 WHERE id = ?", (provider_id,))
            conn.commit()

    def get_active_provider(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM providers WHERE is_active = 1").fetchone()
            return dict(row) if row else None

    def set_setting(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
            conn.commit()

    def get_setting(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return json.loads(row[0]) if row else default
