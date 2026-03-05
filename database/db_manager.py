import sqlite3, json
from datetime import datetime, timedelta
from config import Config

class DatabaseManager:
    def __init__(self):
        self.db = Config.DB_PATH
        self._init()

    def _c(self):
        c = sqlite3.connect(self.db); c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL"); return c

    def _init(self):
        c = self._c(); x = c.cursor()
        x.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE NOT NULL,
            username TEXT, preferred_site INTEGER DEFAULT 1,
            preferred_quality TEXT DEFAULT '720p', preferred_server TEXT DEFAULT 'auto',
            total_downloads INTEGER DEFAULT 0, state_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        x.execute("""CREATE TABLE IF NOT EXISTS wa_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT UNIQUE NOT NULL,
            session_data TEXT, is_active INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        x.execute("""CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_phone TEXT NOT NULL,
            anime_title TEXT, episode_number REAL, season_number INTEGER,
            site_name TEXT, quality TEXT, server TEXT, file_size_mb REAL,
            compressed_size_mb REAL, file_path TEXT, status TEXT DEFAULT 'pending',
            error_msg TEXT, started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP, sent_at TIMESTAMP)""")
        x.execute("""CREATE TABLE IF NOT EXISTS cache (
            cache_key TEXT PRIMARY KEY, cache_value TEXT, expires_at TIMESTAMP)""")
        x.execute("""CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, message TEXT,
            phone TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        x.execute("CREATE INDEX IF NOT EXISTS idx_up ON users(phone)")
        x.execute("CREATE INDEX IF NOT EXISTS idx_dp ON downloads(user_phone)")
        c.commit(); c.close()

    def get_or_create_user(self, phone, username=None):
        c = self._c(); x = c.cursor()
        x.execute("SELECT * FROM users WHERE phone=?", (phone,))
        u = x.fetchone()
        if not u:
            x.execute("INSERT INTO users (phone,username) VALUES (?,?)", (phone, username))
            c.commit(); x.execute("SELECT * FROM users WHERE phone=?", (phone,)); u = x.fetchone()
        c.close(); return dict(u)

    def update_user(self, phone, **kw):
        c = self._c()
        s = ", ".join(f"{k}=?" for k in kw); v = list(kw.values()) + [phone]
        c.execute(f"UPDATE users SET {s}, last_active=CURRENT_TIMESTAMP WHERE phone=?", v)
        c.commit(); c.close()

    def get_state(self, phone):
        c = self._c(); x = c.cursor()
        x.execute("SELECT state_data FROM users WHERE phone=?", (phone,))
        r = x.fetchone(); c.close()
        if r and r["state_data"]:
            try: return json.loads(r["state_data"])
            except: pass
        return {}

    def set_state(self, phone, state):
        self.update_user(phone, state_data=json.dumps(state, ensure_ascii=False))

    def clear_state(self, phone): self.set_state(phone, {})

    def save_download(self, d):
        c = self._c(); x = c.cursor()
        x.execute("""INSERT INTO downloads (user_phone,anime_title,episode_number,season_number,site_name,quality,server,status)
            VALUES (?,?,?,?,?,?,?,?)""",
            (d.get("phone"), d.get("anime_title"), d.get("ep_num"), d.get("season_num"),
             d.get("site"), d.get("quality"), d.get("server"), "pending"))
        i = x.lastrowid; c.commit(); c.close(); return i

    def update_download(self, dl_id, **kw):
        c = self._c()
        s = ", ".join(f"{k}=?" for k in kw); v = list(kw.values()) + [dl_id]
        c.execute(f"UPDATE downloads SET {s} WHERE id=?", v); c.commit(); c.close()

    def save_session(self, sid, data):
        c = self._c()
        c.execute("INSERT OR REPLACE INTO wa_sessions (session_id,session_data,is_active,updated_at) VALUES (?,?,1,CURRENT_TIMESTAMP)", (sid, data))
        c.commit(); c.close()

    def get_cache(self, key):
        c = self._c(); x = c.cursor()
        x.execute("SELECT cache_value FROM cache WHERE cache_key=? AND (expires_at IS NULL OR expires_at>?)",
                  (key, datetime.now().isoformat()))
        r = x.fetchone(); c.close()
        if r:
            try: return json.loads(r["cache_value"])
            except: return r["cache_value"]
        return None

    def set_cache(self, key, val, hours=24):
        c = self._c()
        c.execute("INSERT OR REPLACE INTO cache (cache_key,cache_value,expires_at) VALUES (?,?,?)",
                  (key, json.dumps(val, ensure_ascii=False), (datetime.now()+timedelta(hours=hours)).isoformat()))
        c.commit(); c.close()

    def log(self, level, msg, phone=None):
        try:
            c = self._c()
            c.execute("INSERT INTO logs (level,message,phone) VALUES (?,?,?)", (level, msg, phone))
            c.commit(); c.close()
        except: pass

    def get_stats(self):
        c = self._c(); x = c.cursor(); s = {}
        x.execute("SELECT COUNT(*) n FROM users"); s["users"] = x.fetchone()["n"]
        x.execute("SELECT COUNT(*) n FROM downloads"); s["downloads"] = x.fetchone()["n"]
        x.execute("SELECT COUNT(*) n FROM downloads WHERE status='completed'"); s["completed"] = x.fetchone()["n"]
        c.close(); return s