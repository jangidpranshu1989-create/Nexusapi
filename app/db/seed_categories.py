import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "nexus.db")

def seed():
    categories_to_seed = [
        ("File Converters", "file-converters", "file"),
        ("Authentication", "authentication", "lock"),
        ("Payment Processing", "payments", "credit-card"),
        ("Notifications", "notifications", "bell"),
        ("Web Scraping", "web-scraping", "search"),
        ("Image Processing", "image-processing", "image"),
        ("Utility", "utility", "tool"),
        ("Data Analytics", "analytics", "bar-chart")
    ]
    
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted_count = 0
    skipped_count = 0
    
    for name, slug, icon in categories_to_seed:
        cursor.execute("SELECT id FROM categories WHERE slug = ?", (slug,))
        if cursor.fetchone():
            skipped_count += 1
            continue
            
        cursor.execute(
            "INSERT INTO categories (name, slug, icon, count) VALUES (?, ?, ?, 0)",
            (name, slug, icon)
        )
        inserted_count += 1
        
    conn.commit()
    conn.close()
    
    print(f"Seed complete. Inserted: {inserted_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    seed()
