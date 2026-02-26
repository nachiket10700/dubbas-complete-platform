import sqlite3
import os

def init_database():
    """Initialize all database tables"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'dabbas.db')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"📁 Creating tables in: {db_path}")
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            role TEXT NOT NULL,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            email_verified BOOLEAN DEFAULT 0,
            phone_verified BOOLEAN DEFAULT 0
        )
    ''')
    print("✅ users table created")
    
    # Create customer_preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_preferences (
            user_id TEXT PRIMARY KEY,
            dietary_restrictions TEXT,
            favorite_cuisines TEXT,
            disliked_ingredients TEXT,
            health_goals TEXT,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("✅ customer_preferences table created")
    
    # Create providers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS providers (
            user_id TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            business_address TEXT,
            phone TEXT,
            gst_number TEXT,
            fssai_license TEXT,
            cuisine_specialties TEXT,
            service_area TEXT,
            delivery_radius INTEGER DEFAULT 5,
            commission_rate REAL DEFAULT 0.15,
            rating REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            is_verified BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("✅ providers table created")
    
    # Create menu_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            provider_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            cuisine TEXT,
            ingredients TEXT,
            tags TEXT,
            is_vegetarian BOOLEAN DEFAULT 0,
            is_available BOOLEAN DEFAULT 1,
            is_popular BOOLEAN DEFAULT 0,
            order_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE CASCADE
        )
    ''')
    print("✅ menu_items table created")
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            items TEXT,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            delivery_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE CASCADE
        )
    ''')
    print("✅ orders table created")
    
    # Create user_ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ratings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            meal_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )
    ''')
    print("✅ user_ratings table created")
    
    # Create user_interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            meal_id TEXT NOT NULL,
            action TEXT,
            rating INTEGER,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )
    ''')
    print("✅ user_interactions table created")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 All database tables created successfully!")

def add_sample_user():
    """Add a sample user for testing"""
    import hashlib
    import secrets
    from datetime import datetime
    
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'dabbas.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", ("test@example.com",))
    if cursor.fetchone():
        print("✅ Sample user already exists")
        conn.close()
        return
    
    # Create sample user
    user_id = f"USR{secrets.token_hex(4).upper()}"
    password_hash = hashlib.sha256("password123".encode()).hexdigest()
    
    cursor.execute('''
        INSERT INTO users (id, username, email, password_hash, phone, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, "Test User", "test@example.com", password_hash, "9876543210", "customer", datetime.now()))
    
    conn.commit()
    conn.close()
    print("✅ Sample user created - Email: test@example.com, Password: password123")

if __name__ == "__main__":
    init_database()
    add_sample_user()