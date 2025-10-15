import sqlite3
import os

DB_PATH = "data/products.db"  # Match the path from build_index.py

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]
    print(f"Total products in database: {count}")
    
    # Get sample of products
    c.execute("SELECT id, name, category FROM products LIMIT 5")
    print("\nSample of products:")
    for row in c.fetchall():
        print(f"ID: {row[0]}, Name: {row[1]}, Category: {row[2]}")
        
    conn.close()

if __name__ == "__main__":
    check_database()