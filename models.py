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

# Constants for user statuses
USER_STATUS_READY_TO_CHAT = "ready_to_chat"
USER_STATUS_NOT_READY_TO_CHAT = "not_ready_to_chat"

# User Model
class User:
    def __init__(self, id, status):
        self.id = id
        self.status = status

# Function to get a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return conn

# Function to add a new user to the database
async def add_user_to_database(user_id: int, status: str):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (id, status) VALUES (?, ?)', (user_id, status))
        conn.commit()
    finally:
        conn.close()

# Function to get user status from the database
async def get_user_status(user_id: int) -> str:
    conn = get_db_connection()
    try:
        user = conn.execute('SELECT status FROM users WHERE id = ?', (user_id,)).fetchone()
        return user['status'] if user else None
    finally:
        conn.close()

# Function to update user status in the database
async def update_user_status(user_id: int, status: str):
    conn = get_db_connection()
    try:
        conn.execute('UPDATE users SET status = ? WHERE id = ?', (status, user_id))
        conn.commit()
    finally:
        conn.close()