"""
Database Migration Script
Adds user_id columns to existing tickets and meetings tables
"""
import sqlite3
import os

DB_PATH = "enterprise_db.sqlite"

def migrate_database():
    """Add user_id columns to existing tables if they don't exist"""
    
    if not os.path.exists(DB_PATH):
        print("✅ No existing database found. Will be created on first run.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column exists in tickets table
        cursor.execute("PRAGMA table_info(tickets)")
        tickets_columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in tickets_columns:
            print("📝 Adding user_id column to tickets table...")
            cursor.execute("ALTER TABLE tickets ADD COLUMN user_id INTEGER")
            print("✅ tickets table updated")
        else:
            print("✅ tickets table already has user_id column")
        
        # Check if user_id column exists in meetings table
        cursor.execute("PRAGMA table_info(meetings)")
        meetings_columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in meetings_columns:
            print("📝 Adding user_id column to meetings table...")
            cursor.execute("ALTER TABLE meetings ADD COLUMN user_id INTEGER")
            print("✅ meetings table updated")
        else:
            print("✅ meetings table already has user_id column")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...\n")
    migrate_database()
