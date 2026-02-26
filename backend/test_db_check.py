import os
import sqlite3

# Check if the database exists
db_path = r'C:\Users\PRANJAL\dabbas-complete-platform\backend\database\dabbas.db'
print(f"Database exists: {os.path.exists(db_path)}")
print(f"Database path: {db_path}")

if os.path.exists(db_path):
    print(f"File size: {os.path.getsize(db_path)} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check users table specifically
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table = cursor.fetchone()
    print(f"\n👤 Users table exists: {table is not None}")
    
    if table:
        # Show users table structure
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("\n📊 Users table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\n👥 Total users: {count}")
    
    conn.close()
else:
    print("❌ Database file does not exist!")