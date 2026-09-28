import sqlite3
from contextlib import contextmanager

DB_FILE = 'assistant.db'

@contextmanager
def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS bookings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            name TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS sessions(
            phone TEXT PRIMARY KEY,
            state TEXT DEFAULT 'idle',
            temp_data TEXT DEFAULT '{}'
        )''')


# session stuff

def get_session(phone):
    with connect() as c:
        row = c.execute('SELECT * FROM sessions WHERE phone=?', (phone,)).fetchone()
        if row is None:
            # first time user, make a new session
            c.execute("INSERT INTO sessions(phone, state, temp_data) VALUES(?, 'idle', '{}')", (phone,))
            return {'phone': phone, 'state': 'idle', 'temp_data': '{}'}
        return dict(row)

def update_session(phone, state, data='{}'):
    with connect() as c:
        c.execute("""INSERT INTO sessions(phone,state,temp_data) VALUES(?,?,?)
            ON CONFLICT(phone) DO UPDATE SET state=excluded.state, temp_data=excluded.temp_data""",
            (phone, state, data))

def reset_session(phone):
    update_session(phone, 'idle', '{}')


# orders

def add_order(phone, item, qty):
    with connect() as c:
        cur = c.execute('INSERT INTO orders(phone, item, quantity) VALUES(?,?,?)',
                        (phone, item, qty))
        return cur.lastrowid

def get_order(oid):
    with connect() as c:
        row = c.execute('SELECT * FROM orders WHERE id=?', (oid,)).fetchone()
        if row:
            return dict(row)
        return None

def get_orders_for_phone(phone):
    with connect() as c:
        rows = c.execute('SELECT * FROM orders WHERE phone=? ORDER BY created_at DESC',
                         (phone,)).fetchall()
        return [dict(r) for r in rows]

def update_order_status(oid, status):
    with connect() as c:
        cur = c.execute('UPDATE orders SET status=? WHERE id=?', (status, oid))
        return cur.rowcount > 0


# bookings

def add_booking(phone, name, date, time):
    with connect() as c:
        cur = c.execute('INSERT INTO bookings(phone,name,date,time) VALUES(?,?,?,?)',
                        (phone, name, date, time))
        return cur.lastrowid

def is_slot_taken(date, time):
    with connect() as c:
        row = c.execute("SELECT 1 FROM bookings WHERE date=? AND time=? AND status='confirmed'",
                        (date, time)).fetchone()
        return row is not None

def get_bookings_for_phone(phone):
    with connect() as c:
        rows = c.execute("SELECT * FROM bookings WHERE phone=? AND status='confirmed' ORDER BY date,time",
                         (phone,)).fetchall()
        return [dict(r) for r in rows]

def cancel_booking(bid, phone):
    with connect() as c:
        cur = c.execute("UPDATE bookings SET status='cancelled' WHERE id=? AND phone=?",
                        (bid, phone))
        return cur.rowcount > 0