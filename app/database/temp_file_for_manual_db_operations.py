from sqlalchemy import create_engine, text
from app.config import DATABASE_URI
# Assuming DATABASE_URI is your SQLite database URI
engine = create_engine(DATABASE_URI)

# Add the is_active column to the users table
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"))
    conn.commit()