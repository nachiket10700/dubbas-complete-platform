import os
import sqlite3
from datetime import datetime

def init_all_tables():
    """Initialize all database tables"""
    
    # Database path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, 'database', 'dabbas.db')
    
    print(f"📁 Initializing database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            profile_data TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            email_verified BOOLEAN DEFAULT 0,
            phone_verified BOOLEAN DEFAULT 0
        )
    ''')
    print("✅ Users table created")
    
    # Providers table
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
            opening_time TEXT DEFAULT '09:00',
            closing_time TEXT DEFAULT '21:00',
            days_operating TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("✅ Providers table created")
    
    # Menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            provider_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            discounted_price REAL,
            category TEXT,
            cuisine TEXT,
            ingredients TEXT,
            tags TEXT,
            is_vegetarian BOOLEAN DEFAULT 0,
            is_vegan BOOLEAN DEFAULT 0,
            is_gluten_free BOOLEAN DEFAULT 0,
            spicy_level TEXT,
            preparation_time INTEGER,
            calories INTEGER,
            image_url TEXT,
            available_for TEXT,
            is_available BOOLEAN DEFAULT 1,
            is_popular BOOLEAN DEFAULT 0,
            order_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE CASCADE
        )
    ''')
    print("✅ Menu items table created")
    
    # User ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ratings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            meal_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_id) REFERENCES menu_items(id) ON DELETE CASCADE,
            UNIQUE(user_id, meal_id)
        )
    ''')
    print("✅ User ratings table created")
    
    # User interactions table
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
    print("✅ User interactions table created")
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            subscription_id TEXT,
            items TEXT,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            delivery_address TEXT,
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE CASCADE
        )
    ''')
    print("✅ Orders table created")
    
    # Customer preferences table
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
    print("✅ Customer preferences table created")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 All database tables initialized successfully!")

if __name__ == '__main__':
    init_all_tables()