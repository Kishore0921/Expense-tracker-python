import sqlite3
import os


def get_connection():
    # Place the database next to the project so it behaves like the original "expenses.db".
    # This is more transparent for development and keeps the database under version control
    # (when desired). It will be created automatically if it doesn't exist.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(root_dir, "expenses.db")
    return sqlite3.connect(db_path)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password BLOB)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, user_id INTEGER, category TEXT, amount REAL, date TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, user_id INTEGER, month TEXT, amount REAL, FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()
        print("Database Initialized Successfully!")
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    init_db()