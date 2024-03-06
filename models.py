import sqlite3
from config import DATABASE_PATH

def create_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DATABASE_PATH)

def initialize_db():
    """Initialize the database with required tables."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT,
                            registered INTEGER DEFAULT 0,
                            terms_accepted INTEGER DEFAULT 0,
                            messages TEXT)""")  # Store JSON array of messages
        cursor.execute("""CREATE TABLE IF NOT EXISTS chats (
                            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user1_id INTEGER,
                            user2_id INTEGER,
                            start_time DATETIME,
                            end_time DATETIME,
                            active INTEGER DEFAULT 1)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id INTEGER,
                            user_id INTEGER,
                            content TEXT,
                            content_type TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS reactions (
                            reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id INTEGER,
                            message_id INTEGER,
                            user_id INTEGER,
                            reaction TEXT)""")
        conn.commit()
    finally:
        conn.close()