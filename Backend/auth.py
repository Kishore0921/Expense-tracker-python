import bcrypt
from Backend.db import get_connection

def register_user(username, password):
    if len(password) != 8:
        return False, "Password must be 8 characters."
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True, "Success"
    except:
        return False, "Username already exists."
    finally:
        conn.close()

def verify_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
        return result[0] # Returns user_id
    return None