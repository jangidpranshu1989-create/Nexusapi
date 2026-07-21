import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "nexus.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("bio", "TEXT"),
        ("accent_color", "TEXT DEFAULT '#6C5CE7'"),
        ("email_notifications", "INTEGER DEFAULT 1"),
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError:
            print(f"Column already exists: {col_name}")

    conn.commit()
    conn.close()
    print("Settings migration complete.")


if __name__ == "__main__":
    migrate()
