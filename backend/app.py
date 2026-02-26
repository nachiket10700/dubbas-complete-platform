#!/usr/bin/env python3
"""
Dabba's Main Application Entry Point
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, session, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the absolute path to the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(backend_dir, 'logs')

# Create logs directory if it doesn't exist
os.makedirs(logs_dir, exist_ok=True)

# Configure logging with absolute path
log_file = os.path.join(logs_dir, 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24)))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 16 * 1024 * 1024))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Apply proxy fix for production
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Enable CORS
CORS(app, supports_credentials=True, origins=['https://dabbas.com', 'http://localhost:8000'])

# Initialize JWT
jwt = JWTManager(app)

# Rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://redis:6379/0" if os.getenv('REDIS_URL') else "memory://"
)

# ============================================================================
# Import Models and Services
# ============================================================================

# User models
from models.user import User, CustomerManager, ProviderManager, OwnerManager

# Payment models
from models.payment import PaymentProcessor, SubscriptionManager

# Complaint models
from models.complaint import ComplaintManager

# Localization models
from models.localization import TranslationManager, RegionalContentManager

# ============================================================================
# RECOMMENDATION SERVICE
# ============================================================================

from services.recommendation import RecommendationEngine

# Import other services
from services.email_service import EmailService
from services.sms_service import SMSService

# ============================================================================
# Initialize Services
# ============================================================================

# Initialize user-related services
user_model = User()
customer_manager = CustomerManager()
provider_manager = ProviderManager()
owner_manager = OwnerManager()

# Initialize payment services
payment_processor = PaymentProcessor()
subscription_manager = SubscriptionManager()

# Initialize complaint service
complaint_manager = ComplaintManager()

# Initialize localization services
translation_manager = TranslationManager()
regional_manager = RegionalContentManager()

# ============================================================================
# INITIALIZE RECOMMENDATION ENGINE
# ============================================================================

try:
    recommendation_engine = RecommendationEngine()
    logger.info("✅ Recommendation Engine initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Recommendation Engine: {str(e)}")
    # Still create the engine, it will use fallback/default recommendations
    recommendation_engine = RecommendationEngine()

# Initialize communication services
email_service = EmailService()
sms_service = SMSService()

# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'environment': os.getenv('APP_ENV', 'development'),
        'services': {
            'recommendation_engine': 'active' if recommendation_engine else 'degraded'
        }
    }), 200

# ============================================================================
# Helper Functions for Recommendations
# ============================================================================

def get_current_meal_time():
    """Determine current meal time based on hour"""
    hour = datetime.now().hour
    if 5 <= hour < 11:
        return 'breakfast'
    elif 11 <= hour < 15:
        return 'lunch'
    elif 15 <= hour < 18:
        return 'snack'
    else:
        return 'dinner'

def get_user_interaction_history(user_id, limit=50):
    """Get user's interaction history for bandit algorithm"""
    import sqlite3
    conn = sqlite3.connect('database/dabbas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT meal_id, action, created_at 
        FROM user_interactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    
    history = cursor.fetchall()
    conn.close()
    
    return [{
        'meal_id': h[0],
        'action': h[1],
        'timestamp': h[2]
    } for h in history]

def generate_explanation(meal, preferences):
    """Generate human-readable explanation for recommendation"""
    explanations = []
    
    # Check cuisine preference
    if meal.get('cuisine') in preferences.get('favorite_cuisines', []):
        explanations.append(f"Because you love {meal['cuisine']} cuisine")
    
    # Check ingredient preferences
    user_ingredients = set(preferences.get('preferred_ingredients', []))
    meal_ingredients = set(meal.get('ingredients', []))
    matches = user_ingredients.intersection(meal_ingredients)
    
    if matches:
        explanations.append(f"Contains your favorite: {', '.join(list(matches)[:2])}")
    
    # Check dietary preferences
    if preferences.get('dietary_restrictions'):
        if meal.get('is_vegetarian') and 'vegetarian' in preferences['dietary_restrictions']:
            explanations.append("Vegetarian option")
    
    # Popularity based
    if meal.get('is_popular'):
        explanations.append("Popular in your area")
    
    # Order history based
    if meal.get('reorder_frequency', 0) > 3:
        explanations.append("You've ordered this before")
    
    return ' • '.join(explanations) if explanations else "Recommended for you"

# ============================================================================
# RECOMMENDATION ENDPOINTS - CORE FUNCTIONALITY
# ============================================================================

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """
    Get personalized meal recommendations for the logged-in user
    This is the main recommendation endpoint that uses the hybrid algorithm
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user preferences
        preferences = customer_manager.get_preferences(user_id)
        
        # Get user's order history for better recommendations
        order_history = customer_manager.get_recent_orders(user_id, limit=10)
        
        # Get context from query parameters
        city = request.args.get('city', 'mumbai')
        time_of_day = request.args.get('time', get_current_meal_time())
        limit = int(request.args.get('limit', 10))
        
        # Log recommendation request
        logger.info(f"Generating recommendations for user {user_id} in {city} at {time_of_day}")
        
        # Get recommendations from engine
        recommendations = recommendation_engine.get_recommendations(
            user_id=user_id,
            preferences=preferences,
            order_history=order_history,
            city=city,
            time_of_day=time_of_day,
            limit=limit
        )
        
        # Add regional context and explanations
        for rec in recommendations:
            region_info = regional_manager.get_region_info(city)
            rec['explanation'] = generate_explanation(rec, preferences)
            
            # Add regional note in user's preferred language
            user_lang = preferences.get('language', 'en')
            rec['regional_note'] = translation_manager.translate(
                'recommendations.regional_special',
                language=user_lang,
                region=region_info.get('capital', city)
            )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations),
            'context': {
                'city': city,
                'time_of_day': time_of_day,
                'personalized': True
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get recommendations'
        }), 500

@app.route('/api/recommendations/explore', methods=['GET'])
@jwt_required()
def get_explore_recommendations():
    """
    Get exploration recommendations (new/discovery items)
    Uses contextual bandit algorithm for exploration-exploitation tradeoff
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user preferences
        preferences = customer_manager.get_preferences(user_id)
        
        # Get interaction history for bandit algorithm
        interaction_history = get_user_interaction_history(user_id)
        
        # Get exploration recommendations
        recommendations = recommendation_engine.explore_recommendations(
            user_id=user_id,
            preferences=preferences,
            history=interaction_history,
            limit=int(request.args.get('limit', 5))
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'type': 'exploration'
        }), 200
        
    except Exception as e:
        logger.error(f"Explore recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get exploration recommendations'
        }), 500

@app.route('/api/recommendations/similar/<meal_id>', methods=['GET'])
@jwt_required()
def get_similar_recommendations(meal_id):
    """
    Get meals similar to a specific meal
    Uses content-based filtering
    """
    try:
        user_id = get_jwt_identity()
        
        similar_meals = recommendation_engine.get_similar_items(
            meal_id=meal_id,
            user_id=user_id,
            limit=int(request.args.get('limit', 5))
        )
        
        return jsonify({
            'success': True,
            'meal_id': meal_id,
            'similar_meals': similar_meals
        }), 200
        
    except Exception as e:
        logger.error(f"Similar recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get similar meals'
        }), 500

@app.route('/api/recommendations/popular', methods=['GET'])
def get_popular_recommendations():
    """
    Get popular meals (no login required)
    Used for homepage and non-personalized recommendations
    """
    try:
        city = request.args.get('city', 'mumbai')
        limit = int(request.args.get('limit', 10))
        
        popular_meals = recommendation_engine.get_popular_items(
            city=city,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recommendations': popular_meals,
            'type': 'popular'
        }), 200
        
    except Exception as e:
        logger.error(f"Popular recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get popular recommendations'
        }), 500

@app.route('/api/recommendations/trending', methods=['GET'])
def get_trending_recommendations():
    """
    Get trending meals based on recent order activity
    """
    try:
        city = request.args.get('city', 'mumbai')
        limit = int(request.args.get('limit', 10))
        
        trending = recommendation_engine.get_trending_items(
            city=city,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recommendations': trending,
            'type': 'trending'
        }), 200
        
    except Exception as e:
        logger.error(f"Trending recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get trending recommendations'
        }), 500

@app.route('/api/recommendations/feedback', methods=['POST'])
@jwt_required()
def submit_recommendation_feedback():
    """
    Submit feedback on recommendations to improve the algorithm
    This is crucial for the bandit algorithm to learn
    """
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        meal_id = data.get('meal_id')
        liked = data.get('liked')
        rating = data.get('rating')
        context = data.get('context', {})
        
        # Record interaction for bandit algorithm
        recommendation_engine.record_interaction(
            user_id=user_id,
            meal_id=meal_id,
            liked=liked,
            rating=rating,
            context=context
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded. Thank you for helping us improve!'
        }), 200
        
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to record feedback'
        }), 500

# ============================================================================
# Language & Localization Endpoints
# ============================================================================

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get all supported languages"""
    languages = translation_manager.get_available_languages()
    return jsonify({
        'success': True,
        'languages': languages
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all supported cities"""
    cities = regional_manager.get_cities()
    return jsonify({
        'success': True,
        'cities': cities
    })

@app.route('/api/cities/<city>/areas', methods=['GET'])
def get_city_areas(city):
    """Get areas in a specific city"""
    areas = regional_manager.get_areas(city)
    return jsonify({
        'success': True,
        'city': city,
        'areas': areas
    })

@app.route('/api/region/<city>', methods=['GET'])
def get_region_info(city):
    """Get regional information for a city"""
    region = regional_manager.get_region_info(city)
    festive = regional_manager.get_festive_special(region.get('language'))
    
    return jsonify({
        'success': True,
        'region': region,
        'festive_special': festive
    })

@app.route('/api/local-recommendations', methods=['GET'])
def get_local_recommendations():
    """Get local food recommendations based on city and time"""
    city = request.args.get('city', 'mumbai')
    time_of_day = request.args.get('time', get_current_meal_time())
    
    recommendations = regional_manager.get_local_recommendations(city, time_of_day)
    
    return jsonify({
        'success': True,
        'city': city,
        'time_of_day': time_of_day,
        'recommendations': recommendations
    })

# ============================================================================
# Customer Endpoints
# ============================================================================

@app.route('/api/customer/register', methods=['POST'])
@limiter.limit("5 per minute")
def customer_register():
    """Register a new customer"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create user
        result = user_model.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role='customer',
            profile_data={
                'phone': data['phone'],
                'address': data.get('address', ''),
                'city': data.get('city', ''),
                'preferred_language': data.get('language', 'en')
            }
        )
        
        if result['success']:
            # Send welcome email
            email_service.send_welcome_email(data['email'], data['username'])
            
            # Send SMS
            sms_service.send_welcome_sms(data['phone'], data['username'])
            
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Customer registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/customer/login', methods=['POST'])
@limiter.limit("10 per minute")
def customer_login():
    """Customer login"""
    try:
        data = request.json
        
        if 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        # Authenticate user
        result = user_model.authenticate(data['email'], data['password'])
        
        if result['success']:
            # Create JWT token
            access_token = create_access_token(
                identity=result['user_id'],
                additional_claims={'role': 'customer'}
            )
            
            result['token'] = access_token
            
            # Load customer preferences
            preferences = customer_manager.get_preferences(result['user_id'])
            result['preferences'] = preferences
            
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"Customer login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/customer/profile', methods=['GET'])
@jwt_required()
def get_customer_profile():
    """Get customer profile"""
    try:
        user_id = get_jwt_identity()
        
        # Get user details
        user = user_model.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get preferences
        preferences = customer_manager.get_preferences(user_id)
        
        # Get active subscriptions
        subscriptions = subscription_manager.get_user_subscriptions(user_id)
        
        # Get recent orders
        orders = customer_manager.get_recent_orders(user_id, limit=5)
        
        return jsonify({
            'success': True,
            'profile': user,
            'preferences': preferences,
            'subscriptions': subscriptions,
            'recent_orders': orders
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load profile'
        }), 500

@app.route('/api/customer/profile', methods=['PUT'])
@jwt_required()
def update_customer_profile():
    """Update customer profile"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Update user
        result = user_model.update_user(user_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile'
        }), 500

@app.route('/api/customer/preferences', methods=['POST'])
@jwt_required()
def save_customer_preferences():
    """Save customer preferences"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        result = customer_manager.save_preferences(user_id, data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Save preferences error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save preferences'
        }), 500

@app.route('/api/customer/subscriptions', methods=['GET'])
@jwt_required()
def get_customer_subscriptions():
    """Get customer subscriptions"""
    try:
        user_id = get_jwt_identity()
        
        subscriptions = subscription_manager.get_user_subscriptions(user_id)
        
        return jsonify({
            'success': True,
            'subscriptions': subscriptions
        }), 200
        
    except Exception as e:
        logger.error(f"Get subscriptions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load subscriptions'
        }), 500

@app.route('/api/customer/subscribe', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a new subscription"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if 'plan_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Plan type required'
            }), 400
        
        # Get provider preference if any
        provider_id = data.get('provider_id')
        
        # Create subscription
        result = subscription_manager.create_subscription(
            user_id=user_id,
            plan_type=data['plan_type'],
            provider_id=provider_id
        )
        
        if result['success']:
            # Send confirmation
            user = user_model.get_user_by_id(user_id)
            email_service.send_subscription_confirmation(
                user['email'],
                user['username'],
                result['plan']
            )
            
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Create subscription error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create subscription'
        }), 500

@app.route('/api/customer/subscription/<subscription_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        user_id = get_jwt_identity()
        
        # Verify subscription belongs to user
        subscriptions = subscription_manager.get_user_subscriptions(user_id)
        if not any(s['id'] == subscription_id for s in subscriptions):
            return jsonify({
                'success': False,
                'error': 'Subscription not found'
            }), 404
        
        result = subscription_manager.cancel_subscription(subscription_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Cancel subscription error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to cancel subscription'
        }), 500

@app.route('/api/customer/orders', methods=['GET'])
@jwt_required()
def get_customer_orders():
    """Get customer orders"""
    try:
        user_id = get_jwt_identity()
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        orders = customer_manager.get_orders(user_id, page=page, limit=limit)
        
        return jsonify({
            'success': True,
            'orders': orders,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load orders'
        }), 500

@app.route('/api/customer/order/<order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """Get order details"""
    try:
        user_id = get_jwt_identity()
        
        order = customer_manager.get_order_details(order_id, user_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'order': order
        }), 200
        
    except Exception as e:
        logger.error(f"Get order details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load order details'
        }), 500

# ============================================================================
# Provider Endpoints
# ============================================================================

@app.route('/api/provider/register', methods=['POST'])
@limiter.limit("3 per hour")
def provider_register():
    """Register a new service provider"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'phone', 'business_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create user
        result = user_model.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role='provider',
            profile_data={
                'phone': data['phone'],
                'business_name': data['business_name'],
                'status': 'pending'
            }
        )
        
        if result['success']:
            # Register provider details
            provider_result = provider_manager.register_provider(
                user_id=result['user_id'],
                business_details=data
            )
            
            if provider_result['success']:
                # Send notification to owner
                owner_manager.notify_new_provider(result['user_id'], data['business_name'])
                
                # Send confirmation email
                email_service.send_provider_registration_confirmation(
                    data['email'],
                    data['business_name']
                )
                
                return jsonify({
                    'success': True,
                    'user_id': result['user_id'],
                    'message': 'Provider registered successfully. Pending verification.'
                }), 201
            else:
                return jsonify(provider_result), 400
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Provider registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/provider/login', methods=['POST'])
@limiter.limit("10 per minute")
def provider_login():
    """Provider login"""
    try:
        data = request.json
        
        if 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        result = user_model.authenticate(data['email'], data['password'])
        
        if result['success'] and result['role'] == 'provider':
            # Create JWT token
            access_token = create_access_token(
                identity=result['user_id'],
                additional_claims={'role': 'provider'}
            )
            
            result['token'] = access_token
            
            # Get provider stats
            stats = provider_manager.get_provider_stats(result['user_id'])
            result['stats'] = stats
            
            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials or not a provider account'
            }), 401
            
    except Exception as e:
        logger.error(f"Provider login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/provider/dashboard', methods=['GET'])
@jwt_required()
def provider_dashboard():
    """Get provider dashboard data"""
    try:
        provider_id = get_jwt_identity()
        
        # Get stats
        stats = provider_manager.get_provider_stats(provider_id)
        
        # Get today's orders
        today_orders = provider_manager.get_today_orders(provider_id)
        
        # Get menu items
        menu = provider_manager.get_menu(provider_id)
        
        # Get recent complaints
        complaints = complaint_manager.get_complaints(provider_id=provider_id, limit=5)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'today_orders': today_orders,
            'menu': menu,
            'recent_complaints': complaints
        }), 200
        
    except Exception as e:
        logger.error(f"Provider dashboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load dashboard'
        }), 500

@app.route('/api/provider/menu', methods=['GET'])
@jwt_required()
def get_provider_menu():
    """Get provider menu"""
    try:
        provider_id = get_jwt_identity()
        
        menu = provider_manager.get_menu(provider_id)
        
        return jsonify({
            'success': True,
            'menu': menu
        }), 200
        
    except Exception as e:
        logger.error(f"Get menu error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load menu'
        }), 500

@app.route('/api/provider/menu', methods=['POST'])
@jwt_required()
def add_menu_item():
    """Add menu item"""
    try:
        provider_id = get_jwt_identity()
        data = request.json
        
        result = provider_manager.add_menu_item(provider_id, data)
        
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Add menu item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to add menu item'
        }), 500

@app.route('/api/provider/menu/<item_id>', methods=['PUT'])
@jwt_required()
def update_menu_item(item_id):
    """Update menu item"""
    try:
        provider_id = get_jwt_identity()
        data = request.json
        
        result = provider_manager.update_menu_item(provider_id, item_id, data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Update menu item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update menu item'
        }), 500

@app.route('/api/provider/menu/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_menu_item(item_id):
    """Delete menu item"""
    try:
        provider_id = get_jwt_identity()
        
        result = provider_manager.delete_menu_item(provider_id, item_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Delete menu item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete menu item'
        }), 500

@app.route('/api/provider/orders', methods=['GET'])
@jwt_required()
def get_provider_orders():
    """Get provider orders"""
    try:
        provider_id = get_jwt_identity()
        
        status = request.args.get('status')
        date = request.args.get('date')
        
        orders = provider_manager.get_orders(provider_id, status=status, date=date)
        
        return jsonify({
            'success': True,
            'orders': orders
        }), 200
        
    except Exception as e:
        logger.error(f"Get orders error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load orders'
        }), 500

@app.route('/api/provider/order/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status"""
    try:
        provider_id = get_jwt_identity()
        data = request.json
        
        if 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status required'
            }), 400
        
        result = provider_manager.update_order_status(
            provider_id, order_id, data['status']
        )
        
        if result['success']:
            # Notify customer
            customer_id = result.get('customer_id')
            if customer_id:
                customer = user_model.get_user_by_id(customer_id)
                if customer:
                    sms_service.send_order_status_update(
                        customer['phone'],
                        order_id,
                        data['status']
                    )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Update order status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update order status'
        }), 500

@app.route('/api/provider/earnings', methods=['GET'])
@jwt_required()
def get_provider_earnings():
    """Get provider earnings"""
    try:
        provider_id = get_jwt_identity()
        
        period = request.args.get('period', 'month')
        
        earnings = provider_manager.get_earnings(provider_id, period)
        
        return jsonify({
            'success': True,
            'earnings': earnings
        }), 200
        
    except Exception as e:
        logger.error(f"Get earnings error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load earnings'
        }), 500

# ============================================================================
# Owner Endpoints
# ============================================================================

@app.route('/api/owner/login', methods=['POST'])
@limiter.limit("5 per minute")
def owner_login():
    """Owner login"""
    try:
        data = request.json
        
        if 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        result = user_model.authenticate(data['email'], data['password'])
        
        if result['success'] and result['role'] == 'owner':
            # Create JWT token
            access_token = create_access_token(
                identity=result['user_id'],
                additional_claims={'role': 'owner'}
            )
            
            result['token'] = access_token
            
            # Get platform stats
            stats = owner_manager.get_platform_stats()
            result['stats'] = stats
            
            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials or not an owner account'
            }), 401
            
    except Exception as e:
        logger.error(f"Owner login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/owner/stats', methods=['GET'])
@jwt_required()
def get_platform_stats():
    """Get platform statistics"""
    try:
        stats = owner_manager.get_platform_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Get platform stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load statistics'
        }), 500

@app.route('/api/owner/providers', methods=['GET'])
@jwt_required()
def get_providers():
    """Get all providers"""
    try:
        status = request.args.get('status')
        verified = request.args.get('verified')
        
        providers = owner_manager.get_providers(status=status, verified=verified)
        
        return jsonify({
            'success': True,
            'providers': providers
        }), 200
        
    except Exception as e:
        logger.error(f"Get providers error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load providers'
        }), 500

@app.route('/api/owner/provider/<provider_id>/verify', methods=['POST'])
@jwt_required()
def verify_provider(provider_id):
    """Verify a provider"""
    try:
        data = request.json
        action = data.get('action', 'verify')
        
        if action == 'verify':
            result = owner_manager.verify_provider(provider_id)
        elif action == 'reject':
            result = owner_manager.reject_provider(provider_id, data.get('reason'))
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action'
            }), 400
        
        if result['success']:
            # Notify provider
            provider = user_model.get_user_by_id(provider_id)
            if provider:
                if action == 'verify':
                    email_service.send_provider_verification_confirmation(
                        provider['email'],
                        provider.get('business_name', 'Your business')
                    )
                    sms_service.send_verification_sms(
                        provider['phone'],
                        provider.get('business_name', 'Your business')
                    )
                else:
                    email_service.send_provider_rejection_notification(
                        provider['email'],
                        provider.get('business_name', 'Your business'),
                        data.get('reason')
                    )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Verify provider error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to verify provider'
        }), 500

@app.route('/api/owner/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        customers = owner_manager.get_customers(page=page, limit=limit)
        
        return jsonify({
            'success': True,
            'customers': customers,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Get customers error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load customers'
        }), 500

@app.route('/api/owner/complaints', methods=['GET'])
@jwt_required()
def get_all_complaints():
    """Get all complaints"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        complaints = complaint_manager.get_complaints(
            status=status,
            priority=priority
        )
        
        return jsonify({
            'success': True,
            'complaints': complaints
        }), 200
        
    except Exception as e:
        logger.error(f"Get all complaints error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load complaints'
        }), 500

@app.route('/api/owner/complaint/<complaint_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_complaint(complaint_id):
    """Resolve a complaint"""
    try:
        owner_id = get_jwt_identity()
        data = request.json
        
        result = complaint_manager.resolve_complaint(
            complaint_id,
            data.get('resolution', ''),
            owner_id
        )
        
        if result['success']:
            # Notify involved parties
            complaint = complaint_manager.get_complaint_details(complaint_id)
            if complaint:
                # Notify customer
                customer = user_model.get_user_by_id(complaint['user_id'])
                if customer:
                    email_service.send_complaint_resolved(
                        customer['email'],
                        complaint_id,
                        data.get('resolution')
                    )
                
                # Notify provider if applicable
                if complaint.get('provider_id'):
                    provider = user_model.get_user_by_id(complaint['provider_id'])
                    if provider:
                        email_service.send_complaint_resolved_provider(
                            provider['email'],
                            complaint_id,
                            data.get('resolution')
                        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Resolve complaint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to resolve complaint'
        }), 500

@app.route('/api/owner/settings', methods=['GET'])
@jwt_required()
def get_platform_settings():
    """Get platform settings"""
    try:
        settings = owner_manager.get_settings()
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
        
    except Exception as e:
        logger.error(f"Get settings error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load settings'
        }), 500

@app.route('/api/owner/settings', methods=['PUT'])
@jwt_required()
def update_platform_settings():
    """Update platform settings"""
    try:
        data = request.json
        
        result = owner_manager.update_settings(data)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update settings'
        }), 500

# ============================================================================
# Payment Endpoints
# ============================================================================

@app.route('/api/payment/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create a payment order"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if 'amount' not in data:
            return jsonify({
                'success': False,
                'error': 'Amount required'
            }), 400
        
        # Create Razorpay order
        result = payment_processor.create_payment_order(
            amount=data['amount'],
            currency=data.get('currency', 'INR'),
            receipt=data.get('receipt')
        )
        
        if result['success']:
            # Store order in database
            payment_processor.save_order({
                'user_id': user_id,
                'order_id': result['order_id'],
                'amount': data['amount'],
                'status': 'created'
            })
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Create payment order error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create payment order'
        }), 500

@app.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    """Verify payment signature"""
    try:
        data = request.json
        
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Verify payment
        result = payment_processor.verify_payment(
            data['razorpay_order_id'],
            data['razorpay_payment_id'],
            data['razorpay_signature']
        )
        
        if result['success']:
            # Update subscription if this was for a subscription
            if 'subscription_id' in data:
                subscription_manager.activate_subscription(data['subscription_id'])
            
            # Send confirmation
            user_id = get_jwt_identity() if request.headers.get('Authorization') else None
            if user_id:
                user = user_model.get_user_by_id(user_id)
                if user:
                    email_service.send_payment_confirmation(
                        user['email'],
                        data['razorpay_payment_id'],
                        data.get('amount', 0)
                    )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Verify payment error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Payment verification failed'
        }), 500

@app.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    """Razorpay webhook handler"""
    try:
        data = request.json
        signature = request.headers.get('X-Razorpay-Signature')
        
        # Verify webhook signature
        if not payment_processor.verify_webhook_signature(data, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook event
        event = data.get('event')
        payload = data.get('payload', {})
        
        if event == 'payment.captured':
            # Handle successful payment
            payment_id = payload.get('payment', {}).get('id')
            order_id = payload.get('payment', {}).get('order_id')
            
            payment_processor.update_payment_status(payment_id, 'completed')
            
            # Update any related orders/subscriptions
            # ...
            
        elif event == 'payment.failed':
            # Handle failed payment
            payment_id = payload.get('payment', {}).get('id')
            payment_processor.update_payment_status(payment_id, 'failed')
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Payment webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

# ============================================================================
# Complaint Endpoints
# ============================================================================

@app.route('/api/complaints/create', methods=['POST'])
@jwt_required()
def create_complaint():
    """Create a new complaint"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Get user role
        user = user_model.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        result = complaint_manager.create_complaint(
            user_id=user_id,
            user_role=user['role'],
            data=data
        )
        
        if result['success']:
            # Send notifications
            email_service.send_complaint_confirmation(
                user['email'],
                result['complaint_id']
            )
            
            # Notify provider if applicable
            if data.get('provider_id'):
                provider = user_model.get_user_by_id(data['provider_id'])
                if provider:
                    email_service.send_new_complaint_notification(
                        provider['email'],
                        result['complaint_id']
                    )
        
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Create complaint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create complaint'
        }), 500

@app.route('/api/complaints', methods=['GET'])
@jwt_required()
def get_complaints():
    """Get complaints (filtered by role)"""
    try:
        user_id = get_jwt_identity()
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Filter based on role
        if user['role'] == 'customer':
            complaints = complaint_manager.get_complaints(user_id=user_id)
        elif user['role'] == 'provider':
            complaints = complaint_manager.get_complaints(provider_id=user_id)
        elif user['role'] == 'owner':
            complaints = complaint_manager.get_complaints()
        else:
            complaints = []
        
        return jsonify({
            'success': True,
            'complaints': complaints
        }), 200
        
    except Exception as e:
        logger.error(f"Get complaints error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load complaints'
        }), 500

@app.route('/api/complaints/<complaint_id>', methods=['GET'])
@jwt_required()
def get_complaint_details(complaint_id):
    """Get complaint details"""
    try:
        user_id = get_jwt_identity()
        user = user_model.get_user_by_id(user_id)
        
        complaint = complaint_manager.get_complaint_details(complaint_id)
        
        if not complaint:
            return jsonify({
                'success': False,
                'error': 'Complaint not found'
            }), 404
        
        # Check authorization
        if user['role'] == 'customer' and complaint['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        if user['role'] == 'provider' and complaint.get('provider_id') != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        return jsonify({
            'success': True,
            'complaint': complaint
        }), 200
        
    except Exception as e:
        logger.error(f"Get complaint details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load complaint details'
        }), 500

@app.route('/api/complaints/<complaint_id>/message', methods=['POST'])
@jwt_required()
def add_complaint_message(complaint_id):
    """Add message to complaint"""
    try:
        user_id = get_jwt_identity()
        user = user_model.get_user_by_id(user_id)
        data = request.json
        
        if 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message required'
            }), 400
        
        result = complaint_manager.add_message(
            complaint_id=complaint_id,
            user_id=user_id,
            user_role=user['role'],
            message=data['message'],
            attachments=data.get('attachments')
        )
        
        if result['success']:
            # Notify other parties
            complaint = complaint_manager.get_complaint_details(complaint_id)
            if complaint:
                # Notify customer if message from provider/owner
                if user['role'] != 'customer':
                    customer = user_model.get_user_by_id(complaint['user_id'])
                    if customer:
                        email_service.send_complaint_update(
                            customer['email'],
                            complaint_id
                        )
                
                # Notify provider if message from customer/owner
                if user['role'] != 'provider' and complaint.get('provider_id'):
                    provider = user_model.get_user_by_id(complaint['provider_id'])
                    if provider:
                        email_service.send_complaint_update(
                            provider['email'],
                            complaint_id
                        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Add complaint message error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to add message'
        }), 500

@app.route('/api/complaints/<complaint_id>/escalate', methods=['POST'])
@jwt_required()
def escalate_complaint(complaint_id):
    """Escalate complaint"""
    try:
        user_id = get_jwt_identity()
        user = user_model.get_user_by_id(user_id)
        data = request.json
        
        # Only customers and providers can escalate
        if user['role'] not in ['customer', 'provider']:
            return jsonify({
                'success': False,
                'error': 'Only customers and providers can escalate complaints'
            }), 403
        
        result = complaint_manager.escalate_complaint(
            complaint_id=complaint_id,
            escalated_by=user_id,
            reason=data.get('reason', 'No reason provided')
        )
        
        if result['success']:
            # Notify owner
            owners = user_model.get_users_by_role('owner')
            for owner in owners:
                email_service.send_escalated_complaint_notification(
                    owner['email'],
                    complaint_id
                )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Escalate complaint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to escalate complaint'
        }), 500

# ============================================================================
# Provider Search Endpoints
# ============================================================================

@app.route('/api/providers/nearby', methods=['GET'])
def get_nearby_providers():
    """Get nearby providers based on location"""
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 10, type=int)
        
        if not lat or not lng:
            # Return providers by city if no coordinates
            city = request.args.get('city', 'mumbai')
            providers = provider_manager.get_providers_by_city(city)
        else:
            providers = provider_manager.get_nearby_providers(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'providers': providers
        }), 200
        
    except Exception as e:
        logger.error(f"Get nearby providers error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get nearby providers'
        }), 500

# ============================================================================
# Search Endpoints
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search():
    """Global search across meals and providers"""
    try:
        query = request.args.get('q', '')
        city = request.args.get('city', '')
        cuisine = request.args.get('cuisine', '')
        
        if not query and not cuisine:
            return jsonify({
                'success': False,
                'error': 'Search query or cuisine required'
            }), 400
        
        # Search providers
        providers = provider_manager.search_providers(
            query=query,
            city=city,
            cuisine=cuisine
        )
        
        # Search menu items
        menu_items = provider_manager.search_menu_items(
            query=query,
            cuisine=cuisine
        )
        
        return jsonify({
            'success': True,
            'providers': providers,
            'menu_items': menu_items
        }), 200
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

# ============================================================================
# Contact Endpoint
# ============================================================================

@app.route('/api/contact', methods=['POST'])
@limiter.limit("3 per hour")
def contact():
    """Contact form submission"""
    try:
        data = request.json
        
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Send email to support
        email_service.send_contact_form(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            message=data['message']
        )
        
        # Send auto-reply to user
        email_service.send_contact_auto_reply(
            data['email'],
            data['name']
        )
        
        return jsonify({
            'success': True,
            'message': 'Thank you for contacting us. We will get back to you soon.'
        }), 200
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.'
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# Before Request
# ============================================================================

@app.before_request
def before_request():
    """Set up before each request"""
    # Get language from header or cookie
    language = request.headers.get('Accept-Language', 'en')
    if language not in translation_manager.supported_languages:
        language = 'en'
    
    # Store in g for use in views
    g.language = language

# ============================================================================
# After Request
# ============================================================================

@app.after_request
def after_request(response):
    """Add headers to response"""
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    
    # Add language info
    response.headers.add('Content-Language', g.get('language', 'en'))
    
    return response

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('APP_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
    @app.route("/")
    def home():
     return {
        "success": True,
        "message": "Dabbas Backend Running 🚀"
    }
    
    # Forgot Password endpoints
@app.route('/api/customer/forgot-password', methods=['POST'])
def customer_forgot_password():
    data = request.json
    email = data.get('email')
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expiry = datetime.now() + timedelta(hours=24)
    
    # Store in database (you'll need a password_resets table)
    # db.store_reset_token(email, reset_token, expiry)
    
    # Send email with reset link
    reset_link = f"http://localhost:5000/reset-password?token={reset_token}&role=customer"
    email_service.send_password_reset(email, reset_link)
    
    return jsonify({'success': True, 'message': 'Reset link sent'})

@app.route('/api/provider/forgot-password', methods=['POST'])
def provider_forgot_password():
    # Similar to customer but for providers
    pass

@app.route('/api/owner/forgot-password', methods=['POST'])
def owner_forgot_password():
    # Similar to customer but for owners
    pass

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('password')
    role = data.get('role')
    
    # Verify token
    # user = db.verify_reset_token(token, role)
    # if user:
    #     user.update_password(new_password)
    #     return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid or expired token'})