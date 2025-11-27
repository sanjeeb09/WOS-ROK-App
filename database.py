import sqlite3
import datetime

DB_NAME = "alliance.db"

def initialize_db():
    """Creates all necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Links Table
    c.execute('''CREATE TABLE IF NOT EXISTS links
                 (discord_id INTEGER, game_id TEXT, game_type TEXT, 
                 PRIMARY KEY (discord_id, game_id, game_type))''')
                 
    # 2. History Table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (game_id TEXT, code TEXT, game_type TEXT, 
                 PRIMARY KEY (game_id, code, game_type))''')

    # 3. Stats Table
    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (game_id TEXT, game_type TEXT, date TEXT, level INTEGER, power INTEGER, 
                 PRIMARY KEY (game_id, game_type, date))''')

    # 4. Bear Schedule Table (New)
    c.execute('''CREATE TABLE IF NOT EXISTS bear_schedule
                 (id TEXT PRIMARY KEY, game_type TEXT, trap_number INTEGER, next_time INTEGER, channel_id INTEGER, voice_id INTEGER, status TEXT)''')
                 
    # 5. Bear Pings Config (New)
    c.execute('''CREATE TABLE IF NOT EXISTS bear_pings
                 (game_type TEXT, phase TEXT, setting TEXT, 
                 PRIMARY KEY (game_type, phase))''')
                 
    conn.commit()
    conn.close()

# --- LINKING ---
def add_link(discord_id, game_id, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO links VALUES (?, ?, ?)", (discord_id, str(game_id), game_type))

def remove_link(discord_id, game_id, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.execute("DELETE FROM links WHERE discord_id = ? AND game_id = ? AND game_type = ?", (discord_id, str(game_id), game_type))
        return c.rowcount > 0

def check_discord_link(discord_id, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        res = conn.execute("SELECT game_id FROM links WHERE discord_id = ? AND game_type = ?", (discord_id, game_type)).fetchone()
        return res[0] if res else None

def check_game_id_link(game_id, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        res = conn.execute("SELECT discord_id FROM links WHERE game_id = ? AND game_type = ?", (str(game_id), game_type)).fetchone()
        return res[0] if res else None

def get_linked_user(discord_id, game_type):
    return check_discord_link(discord_id, game_type)

def get_all_users(game_type):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT game_id, discord_id FROM links WHERE game_type = ?", (game_type,)).fetchall()

# --- HISTORY ---
def check_history(game_id, code, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        res = conn.execute("SELECT 1 FROM history WHERE game_id=? AND code=? AND game_type=?", (game_id, code, game_type)).fetchone()
        return res is not None

def add_history(game_id, code, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO history VALUES (?, ?, ?)", (game_id, code, game_type))

# --- STATS ---
def update_stat(game_id, game_type, level, power=0):
    today = datetime.date.today().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO stats VALUES (?, ?, ?, ?, ?)", (str(game_id), game_type, today, level, power))

def get_stat_growth(game_id, game_type):
    with sqlite3.connect(DB_NAME) as conn:
        records = conn.execute("SELECT date, level, power FROM stats WHERE game_id = ? AND game_type = ? ORDER BY date ASC", (str(game_id), game_type)).fetchall()
    if len(records) < 2: return None
    return {"days": len(records), "old_level": records[0][1], "new_level": records[-1][1], "growth": records[-1][1] - records[0][1]}

# --- SCHEDULE ---
def set_bear_schedule(game_type, trap_num, timestamp, channel_id, voice_id):
    unique_id = f"{game_type.lower()}_{trap_num}"
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO bear_schedule VALUES (?, ?, ?, ?, ?, ?, ?)", 
                     (unique_id, game_type, trap_num, timestamp, channel_id, voice_id, "scheduled"))

def get_bear_schedule(game_type):
    """Legacy/Single fetcher."""
    with sqlite3.connect(DB_NAME) as conn:
        res = conn.execute("SELECT next_time, channel_id, voice_id, status FROM bear_schedule WHERE game_type=? LIMIT 1", (game_type,)).fetchone()
        return res

def get_all_schedules():
    """Fetches all traps."""
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT id, game_type, trap_number, next_time, channel_id, voice_id, status FROM bear_schedule").fetchall()

def update_bear_status(game_type, new_status):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE bear_schedule SET status=? WHERE game_type=?", (new_status, game_type))

def update_schedule_status(unique_id, status):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE bear_schedule SET status=? WHERE id=?", (status, unique_id))

def update_schedule_time(unique_id, new_time):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE bear_schedule SET next_time=?, status='scheduled' WHERE id=?", (new_time, unique_id))

def delete_schedule(unique_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.execute("DELETE FROM bear_schedule WHERE id = ?", (unique_id,))
        return c.rowcount > 0

# --- PINGS ---
def set_ping_config(game_type, phase, setting):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO bear_pings VALUES (?, ?, ?)", (game_type, phase, str(setting)))

def get_ping_config(game_type, phase):
    with sqlite3.connect(DB_NAME) as conn:
        res = conn.execute("SELECT setting FROM bear_pings WHERE game_type=? AND phase=?", (game_type, phase)).fetchone()
        return res[0] if res else "0" 

initialize_db()