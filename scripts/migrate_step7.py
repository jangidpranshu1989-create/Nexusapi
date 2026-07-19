import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "nexus.db")

def migrate():
    print(f"Running migration on: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_email_verified INTEGER DEFAULT 0;")
        print("Added is_email_verified column to users.")
    except sqlite3.OperationalError:
        print("is_email_verified column already exists in users.")
        
    try:
        cursor.execute("ALTER TABLE systems ADD COLUMN owner_id INTEGER REFERENCES users(id);")
        print("Added owner_id column to systems.")
    except sqlite3.OperationalError:
        print("owner_id column already exists in systems.")
        
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        code TEXT NOT NULL,
        purpose TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    print("Ensured otp_codes table exists.")
    
    conn.commit()
    conn.close()
    print("Migration Step 7 complete.")

if __name__ == "__main__":
    migrate()
