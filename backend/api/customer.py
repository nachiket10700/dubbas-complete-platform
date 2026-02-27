from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
import sqlite3
import os
@bp.route('/register', methods=['POST'])
def register():
    """Customer registration endpoint"""
    try:
        data = request.json
        print("Registration data received:", data)  # Debug print
        
        # Extract data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        
        # Validate required fields
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate user ID
        import secrets
        user_id = f"USR{secrets.token_hex(4).upper()}"
        
        # Connect to database
        import sqlite3
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'dabbas.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 400
        
        # Insert new user
        from datetime import datetime
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, phone, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, email, password_hash, phone, 'customer', datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Generate JWT token for auto-login
        import jwt
        SECRET_KEY = 'your-secret-key-change-this'  # Use same key as in app.py
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'role': 'customer',
            'exp': datetime.utcnow() + timedelta(days=1)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user_id,
            'username': username,
            'email': email
        }), 201
        
    except Exception as e:
        print("Registration error:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500