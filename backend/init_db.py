# init_db.py
import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize database with all required tables"""
    
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/dubbas.db')
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
    
    # User interactions table (for bandit algorithm)
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
    
    # Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider_id TEXT,
            plan_type TEXT NOT NULL,
            plan_name TEXT NOT NULL,
            price REAL NOT NULL,
            meals_per_day INTEGER NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'active',
            auto_renew BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE SET NULL
        )
    ''')
    
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
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            order_id TEXT,
            subscription_id TEXT,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'INR',
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            gateway_order_id TEXT,
            gateway_payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider_id TEXT,
            order_id TEXT,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES providers(user_id) ON DELETE SET NULL
        )
    ''')
    
    # Complaint messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaint_messages (
            id TEXT PRIMARY KEY,
            complaint_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Languages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS languages (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            native_name TEXT NOT NULL,
            is_rtl BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

def add_sample_data():
    """Add sample data for testing"""
    conn = sqlite3.connect('database/dubbas.db')
    cursor = conn.cursor()
    
    # Add languages
    languages = [
        ('en', 'English', 'English', 0),
        ('hi', 'Hindi', 'हिन्दी', 0),
        ('mr', 'Marathi', 'मराठी', 0),
        ('ta', 'Tamil', 'தமிழ்', 0),
        ('te', 'Telugu', 'తెలుగు', 0),
        ('kn', 'Kannada', 'ಕನ್ನಡ', 0),
        ('ml', 'Malayalam', 'മലയാളം', 0),
        ('bn', 'Bengali', 'বাংলা', 0),
        ('gu', 'Gujarati', 'ગુજરાતી', 0),
        ('pa', 'Punjabi', 'ਪੰਜਾਬੀ', 0),
        ('or', 'Odia', 'ଓଡ଼ିଆ', 0),
        ('as', 'Assamese', 'অসমীয়া', 0),
        ('ur', 'Urdu', 'اردو', 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO languages (code, name, native_name, is_rtl)
        VALUES (?, ?, ?, ?)
    ''', languages)
    
    # Add sample menu items (if no items exist)
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    if cursor.fetchone()[0] == 0:
        sample_items = [
            ('M001', 'Butter Chicken', 'North Indian', 350, 'chicken,butter,cream,spices', 'non-veg,popular', 1, 0, 0, 'medium', 30, 650),
            ('M002', 'Paneer Butter Masala', 'North Indian', 280, 'paneer,butter,cream,tomato', 'veg,popular', 1, 0, 0, 'mild', 25, 550),
            ('M003', 'Masala Dosa', 'South Indian', 120, 'rice,lentils,potato,onion', 'veg,breakfast', 1, 0, 1, 'medium', 15, 300),
            ('M004', 'Vada Pav', 'Maharashtrian', 30, 'potato,bun,spices,chutney', 'veg,snack', 1, 0, 0, 'spicy', 10, 250),
            ('M005', 'Hyderabadi Biryani', 'Hyderabadi', 350, 'rice,chicken,spices,yogurt', 'non-veg,popular', 0, 0, 0, 'spicy', 40, 700),
            ('M006', 'Chole Bhature', 'Punjabi', 180, 'chickpeas,flour,spices,oil', 'veg,popular', 1, 0, 0, 'medium', 25, 600),
            ('M007', 'Idli Sambar', 'South Indian', 80, 'rice,lentils,vegetables', 'veg,breakfast', 1, 0, 1, 'mild', 15, 200),
            ('M008', 'Pav Bhaji', 'Maharashtrian', 150, 'vegetables,bun,butter,spices', 'veg,street food', 1, 0, 0, 'medium', 20, 400),
        ]
        
        for item in sample_items:
            cursor.execute('''
                INSERT INTO menu_items 
                (id, provider_id, name, cuisine, price, ingredients, tags, 
                 is_vegetarian, is_vegan, is_gluten_free, spicy_level, 
                 preparation_time, calories, available_for, is_available)
                VALUES (?, 'PROV001', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '["lunch","dinner"]', 1)
            ''', item)
    
    conn.commit()
    conn.close()
    print("✅ Sample data added successfully!")

if __name__ == '__main__':
    init_database()
    add_sample_data()
    print("\n🎉 Database initialization complete!")
    print("📁 Database location: database/dubbas.db")
    # Change this line in the welcome email section
print("🎉 Database initialization complete for Dabba's!")