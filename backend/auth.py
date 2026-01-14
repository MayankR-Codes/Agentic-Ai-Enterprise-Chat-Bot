import sqlite3
import bcrypt
import os
from datetime import datetime

DB_PATH = "enterprise_db.sqlite"

def init_user_db():
    """Initialize the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password_hash, provided_password):
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password_hash.encode('utf-8'))

def create_user(username, password, full_name, email):
    """Create a new user in the database."""
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)",
                       (username, password_hash, full_name, email))
        conn.commit()
        return {"success": True, "message": "User created successfully"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Username already exists"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def login_user(username, password):
    """Verify user credentials and return user info if valid."""
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash, full_name, email FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(user[2], password):
        return {
            "success": True, 
            "user": {
                "id": user[0],
                "username": user[1],
                "full_name": user[3],
                "email": user[4]
            }
        }
    return {"success": False, "message": "Invalid username or password"}

def get_user_by_username(username):
    """Fetch user information by username for session recovery."""
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, full_name, email FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "full_name": user[2],
            "email": user[3]
        }
    return None