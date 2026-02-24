"""
SMS Service Module
Handles all SMS notifications for the platform
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSService:
    """Handle all SMS notifications"""
    
    def __init__(self):
        self.dev_mode = True
        logger.info("SMS Service initialized (Development Mode)")
    
    def send_sms(self, phone_number: str, message: str):
        """Send an SMS"""
        try:
            if self.dev_mode:
                # Just log the SMS in development
                logger.info(f"📱 SMS TO: {phone_number}")
                logger.info(f"📱 MESSAGE: {message}")
                return True
            
            # In production, integrate with Twilio or other SMS provider
            # client.messages.create(body=message, from_=self.twilio_number, to=phone_number)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return False
    
    def send_welcome_sms(self, phone: str, name: str):
        """Send welcome SMS to new user"""
        message = f"Welcome to Dabba's, {name}! Your account has been created successfully. Download our app to start ordering!"
        return self.send_sms(phone, message)
    
    def send_order_status_update(self, phone: str, order_id: str, status: str):
        """Send order status update"""
        message = f"Your order #{order_id} is now {status}. Track your order in the Dabba's app."
        return self.send_sms(phone, message)
    
    def send_verification_sms(self, phone: str, business_name: str):
        """Send verification SMS to provider"""
        message = f"Congratulations! Your business '{business_name}' has been verified on Dabba's. You can now start receiving orders!"
        return self.send_sms(phone, message)