"""
Payment Processing Module
"""

import json
import secrets
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PaymentProcessor:
    """Handle all payment operations"""
    
    def __init__(self, db_path=None):
        # Get the absolute path to the database
        if db_path is None:
            # Get the backend directory path
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Create database directory if it doesn't exist
            db_dir = os.path.join(backend_dir, 'database')
            os.makedirs(db_dir, exist_ok=True)
            # Set full database path
            self.db_path = os.path.join(db_dir, 'dabbas.db')
        else:
            self.db_path = db_path
        
        print(f"📁 Database path: {self.db_path}")  # Debug output
        self._init_tables()
    
    def _init_tables(self):
        """Initialize payment tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    order_id TEXT,
                    subscription_id TEXT,
                    amount REAL,
                    currency TEXT DEFAULT 'INR',
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    gateway TEXT,
                    gateway_order_id TEXT,
                    gateway_payment_id TEXT,
                    gateway_signature TEXT,
                    refund_id TEXT,
                    refund_amount REAL,
                    refund_reason TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Payment methods table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    method_type TEXT NOT NULL,
                    provider TEXT,
                    last_four TEXT,
                    expiry_month INTEGER,
                    expiry_year INTEGER,
                    card_holder TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    gateway_customer_id TEXT,
                    gateway_payment_method_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Payment tables initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing payment tables: {str(e)}")
            raise
    
    def create_payment_order(self, amount: float, currency: str = 'INR', 
                            receipt: str = None, notes: Dict = None) -> Dict:
        """Create a payment order"""
        try:
            # Mock order creation (since we don't have Razorpay configured yet)
            order_id = f"order_{secrets.token_hex(8)}"
            
            return {
                'success': True,
                'order_id': order_id,
                'amount': int(amount * 100),  # in paise
                'currency': currency,
                'receipt': receipt or f"rcpt_{secrets.token_hex(4)}",
                'status': 'created'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, order_id: str, payment_id: str, signature: str) -> Dict:
        """Verify payment signature"""
        try:
            # Mock verification (always succeeds for development)
            payment_db_id = self._save_payment({
                'gateway_order_id': order_id,
                'gateway_payment_id': payment_id,
                'gateway_signature': signature,
                'status': 'completed',
                'amount': 0  # You'd get this from the order
            })
            
            return {
                'success': True,
                'payment_id': payment_db_id,
                'gateway_payment_id': payment_id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save_payment(self, payment_data: Dict) -> str:
        """Save payment to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        payment_id = f"PAY{secrets.token_hex(4).upper()}"
        
        cursor.execute('''
            INSERT INTO payments 
            (id, user_id, order_id, subscription_id, amount, currency, status,
             gateway, gateway_order_id, gateway_payment_id, gateway_signature,
             metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_id,
            payment_data.get('user_id'),
            payment_data.get('order_id'),
            payment_data.get('subscription_id'),
            payment_data.get('amount', 0),
            payment_data.get('currency', 'INR'),
            payment_data.get('status', 'pending'),
            payment_data.get('gateway', 'razorpay'),
            payment_data.get('gateway_order_id'),
            payment_data.get('gateway_payment_id'),
            payment_data.get('gateway_signature'),
            json.dumps(payment_data.get('metadata', {})),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        return payment_id
    
    def get_payment(self, payment_id: str) -> Optional[Dict]:
        """Get payment details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        
        if payment:
            return {
                'id': payment[0],
                'user_id': payment[1],
                'order_id': payment[2],
                'subscription_id': payment[3],
                'amount': payment[4],
                'currency': payment[5],
                'status': payment[6],
                'created_at': payment[16]
            }
        return None
    
    def get_user_payments(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's payment history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM payments 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        payments = cursor.fetchall()
        conn.close()
        
        return [{
            'id': p[0],
            'amount': p[4],
            'status': p[6],
            'created_at': p[16]
        } for p in payments]
    
    def save_order(self, order_data: Dict):
        """Save order to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        payment_id = f"ORD{secrets.token_hex(4).upper()}"
        
        cursor.execute('''
            INSERT INTO payments 
            (id, user_id, gateway_order_id, amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            payment_id,
            order_data.get('user_id'),
            order_data.get('order_id'),
            order_data.get('amount', 0),
            order_data.get('status', 'created'),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def update_payment_status(self, payment_id: str, status: str):
        """Update payment status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE payments 
            SET status = ?, updated_at = ? 
            WHERE id = ?
        ''', (status, datetime.now(), payment_id))
        
        conn.commit()
        conn.close()
    
    def verify_webhook_signature(self, data: Dict, signature: str) -> bool:
        """Verify webhook signature"""
        # Mock verification for development
        return True


class SubscriptionManager:
    """Manage subscriptions"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(backend_dir, 'database', 'dabbas.db')
        else:
            self.db_path = db_path
            
        self.plans = {
            'daily': {'name': 'Daily Delight', 'price': 99, 'meals_per_day': 1, 'duration_days': 1},
            'weekly': {'name': 'Weekly Warrior', 'price': 599, 'meals_per_day': 1, 'duration_days': 7},
            'monthly': {'name': 'Monthly Master', 'price': 1999, 'meals_per_day': 1, 'duration_days': 30},
            'family_weekly': {'name': 'Family Weekly', 'price': 1499, 'meals_per_day': 3, 'duration_days': 7},
            'family_monthly': {'name': 'Family Monthly', 'price': 4999, 'meals_per_day': 3, 'duration_days': 30}
        }
        self._init_tables()
    
    def _init_tables(self):
        """Initialize subscription tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Subscription tables initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing subscription tables: {str(e)}")
            raise
    
    def create_subscription(self, user_id: str, plan_type: str, 
                           provider_id: str = None, **kwargs) -> Dict:
        """Create a new subscription"""
        if plan_type not in self.plans:
            return {'success': False, 'error': 'Invalid plan type'}
        
        plan = self.plans[plan_type]
        
        # Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        subscription_id = f"SUB{secrets.token_hex(4).upper()}"
        
        cursor.execute('''
            INSERT INTO subscriptions 
            (id, user_id, provider_id, plan_type, plan_name, price, meals_per_day,
             start_date, end_date, auto_renew, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscription_id, user_id, provider_id, plan_type, plan['name'],
            plan['price'], plan['meals_per_day'], start_date, end_date,
            1 if kwargs.get('auto_renew', True) else 0,
            start_date
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'subscription_id': subscription_id,
            'plan': plan,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    
    def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all subscriptions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM subscriptions 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        subscriptions = cursor.fetchall()
        conn.close()
        
        return [{
            'id': s[0],
            'plan_type': s[3],
            'plan_name': s[4],
            'price': s[5],
            'meals_per_day': s[6],
            'start_date': s[7],
            'end_date': s[8],
            'status': s[9]
        } for s in subscriptions]
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM subscriptions WHERE id = ?', (subscription_id,))
        subscription = cursor.fetchone()
        conn.close()
        
        if subscription:
            return {
                'id': subscription[0],
                'user_id': subscription[1],
                'plan_type': subscription[3],
                'plan_name': subscription[4],
                'price': subscription[5],
                'status': subscription[9]
            }
        return None
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel an active subscription"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE subscriptions 
            SET status = 'cancelled', updated_at = ? 
            WHERE id = ?
        ''', (datetime.now(), subscription_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Subscription cancelled'}
    
    def activate_subscription(self, subscription_id: str):
        """Activate a subscription after payment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE subscriptions 
            SET status = 'active', updated_at = ? 
            WHERE id = ?
        ''', (datetime.now(), subscription_id))
        
        conn.commit()
        conn.close()