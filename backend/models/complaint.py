"""
Complaint Management Module
"""

import json
import secrets
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ComplaintStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    REJECTED = 'rejected'
    ESCALATED = 'escalated'

class ComplaintPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'

class ComplaintManager:
    """Handle all complaint operations"""
    
    def __init__(self, db_path=None):
        # Fix the database path
        if db_path is None:
            # Get the absolute path to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Create database directory if it doesn't exist
            db_dir = os.path.join(backend_dir, 'database')
            os.makedirs(db_dir, exist_ok=True)
            # Set full database path
            self.db_path = os.path.join(db_dir, 'dabbas.db')
        else:
            self.db_path = db_path
            
        print(f"📁 Complaint Manager DB Path: {self.db_path}")  # Debug output
        self.categories = {
            'food_quality': 'Food Quality Issue',
            'delivery_delay': 'Delivery Delay',
            'wrong_order': 'Wrong Order',
            'missing_items': 'Missing Items',
            'packaging': 'Packaging Issue',
            'payment': 'Payment Issue',
            'subscription': 'Subscription Issue',
            'staff_behavior': 'Staff Behavior',
            'other': 'Other'
        }
        self._init_tables()
    
    def _init_tables(self):
        """Initialize complaint tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Complaints table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complaints (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    provider_id TEXT,
                    order_id TEXT,
                    subscription_id TEXT,
                    category TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    attachments TEXT,
                    preferred_resolution TEXT,
                    assigned_to TEXT,
                    assigned_at TIMESTAMP,
                    resolved_by TEXT,
                    resolution_notes TEXT,
                    resolved_at TIMESTAMP,
                    escalated_by TEXT,
                    escalated_reason TEXT,
                    escalated_at TIMESTAMP,
                    rating INTEGER,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Complaint messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complaint_messages (
                    id TEXT PRIMARY KEY,
                    complaint_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    attachments TEXT,
                    is_staff_reply BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Complaint tables initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing complaint tables: {str(e)}")
            raise
    
    def create_complaint(self, user_id: str, user_role: str, data: Dict) -> Dict:
        """Create a new complaint"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            complaint_id = f"CMP{secrets.token_hex(4).upper()}"
            
            # Determine priority
            priority = self._determine_priority(
                data.get('category', 'other'),
                data.get('description', '')
            )
            
            cursor.execute('''
                INSERT INTO complaints 
                (id, user_id, user_role, provider_id, order_id, subscription_id,
                 category, subject, description, priority, attachments,
                 preferred_resolution, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                complaint_id, user_id, user_role,
                data.get('provider_id'),
                data.get('order_id'),
                data.get('subscription_id'),
                data.get('category'),
                data.get('subject'),
                data.get('description'),
                priority,
                json.dumps(data.get('attachments', [])),
                data.get('preferred_resolution'),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'complaint_id': complaint_id,
                'priority': priority,
                'status': 'pending'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _determine_priority(self, category: str, description: str) -> str:
        """Determine complaint priority"""
        description = description.lower() if description else ''
        
        # Urgent keywords
        urgent_keywords = ['urgent', 'emergency', 'critical', 'food poisoning', 
                          'sick', 'vomit', 'allergic', 'reaction', 'blood']
        
        high_keywords = ['wrong', 'missing', 'delay', 'cold', 'spoiled', 
                        'rotten', 'smell', 'bad', 'rude', 'abusive']
        
        if any(keyword in description for keyword in urgent_keywords):
            return 'urgent'
        elif category in ['food_quality', 'payment']:
            return 'high'
        elif any(keyword in description for keyword in high_keywords):
            return 'high'
        else:
            return 'medium'
    
    def get_complaints(self, user_id: str = None, provider_id: str = None, 
                      status: str = None, priority: str = None, limit: int = 100) -> List[Dict]:
        """Get complaints with filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM complaints WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if provider_id:
                query += " AND provider_id = ?"
                params.append(provider_id)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            complaints = cursor.fetchall()
            conn.close()
            
            return [self._format_complaint(c) for c in complaints]
            
        except Exception as e:
            print(f"Error getting complaints: {str(e)}")
            return []
    
    def get_complaint_details(self, complaint_id: str) -> Optional[Dict]:
        """Get detailed complaint information with messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get complaint
            cursor.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,))
            complaint = cursor.fetchone()
            
            if not complaint:
                conn.close()
                return None
            
            # Get messages
            cursor.execute('''
                SELECT * FROM complaint_messages 
                WHERE complaint_id = ? 
                ORDER BY created_at ASC
            ''', (complaint_id,))
            messages = cursor.fetchall()
            
            conn.close()
            
            result = self._format_complaint(complaint)
            result['messages'] = [{
                'id': m[0],
                'user_id': m[2],
                'user_role': m[3],
                'message': m[4],
                'attachments': json.loads(m[5]) if m[5] else [],
                'is_staff_reply': bool(m[6]),
                'created_at': m[7]
            } for m in messages]
            
            return result
            
        except Exception as e:
            print(f"Error getting complaint details: {str(e)}")
            return None
    
    def add_message(self, complaint_id: str, user_id: str, user_role: str, 
                   message: str, attachments: List = None) -> Dict:
        """Add a message to complaint thread"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            message_id = f"MSG{secrets.token_hex(4).upper()}"
            is_staff_reply = user_role in ['provider', 'owner']
            
            cursor.execute('''
                INSERT INTO complaint_messages 
                (id, complaint_id, user_id, user_role, message, attachments, is_staff_reply, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (message_id, complaint_id, user_id, user_role, message,
                  json.dumps(attachments or []), is_staff_reply, datetime.now()))
            
            # Update complaint status
            cursor.execute('''
                UPDATE complaints 
                SET status = ?, updated_at = ? 
                WHERE id = ?
            ''', ('in_progress', datetime.now(), complaint_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message_id': message_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def resolve_complaint(self, complaint_id: str, resolution: str, resolved_by: str) -> Dict:
        """Resolve a complaint"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE complaints 
                SET status = ?, resolved_by = ?, resolution_notes = ?, 
                    resolved_at = ?, updated_at = ?
                WHERE id = ?
            ''', ('resolved', resolved_by, resolution, datetime.now(), datetime.now(), complaint_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Complaint resolved'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def escalate_complaint(self, complaint_id: str, escalated_by: str, reason: str) -> Dict:
        """Escalate complaint to higher authority"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE complaints 
                SET status = ?, escalated_by = ?, escalated_reason = ?, 
                    escalated_at = ?, updated_at = ?
                WHERE id = ?
            ''', ('escalated', escalated_by, reason, datetime.now(), datetime.now(), complaint_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Complaint escalated'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _format_complaint(self, complaint_tuple: tuple) -> Dict:
        """Format complaint tuple to dictionary"""
        return {
            'id': complaint_tuple[0],
            'user_id': complaint_tuple[1],
            'user_role': complaint_tuple[2],
            'provider_id': complaint_tuple[3],
            'order_id': complaint_tuple[4],
            'subscription_id': complaint_tuple[5],
            'category': complaint_tuple[6],
            'subject': complaint_tuple[7],
            'description': complaint_tuple[8],
            'priority': complaint_tuple[9],
            'status': complaint_tuple[10],
            'attachments': json.loads(complaint_tuple[11]) if complaint_tuple[11] else [],
            'preferred_resolution': complaint_tuple[12],
            'assigned_to': complaint_tuple[13],
            'assigned_at': complaint_tuple[14],
            'resolved_by': complaint_tuple[15],
            'resolution_notes': complaint_tuple[16],
            'resolved_at': complaint_tuple[17],
            'escalated_by': complaint_tuple[18],
            'escalated_reason': complaint_tuple[19],
            'escalated_at': complaint_tuple[20],
            'rating': complaint_tuple[21],
            'feedback': complaint_tuple[22],
            'created_at': complaint_tuple[23],
            'updated_at': complaint_tuple[24]
        }