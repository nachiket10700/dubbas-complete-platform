import numpy as np
import pandas as pd
import json
import sqlite3
import random
from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContentBasedFiltering:
    """Content-Based Filtering using simple matching"""
    
    def __init__(self, meals_df):
        self.meals_df = meals_df
    
    def get_recommendations(self, user_profile, n=10):
        """Get content-based recommendations based on user profile"""
        try:
            recommendations = []
            preferences = user_profile.get('favorite_cuisines', [])
            
            for _, meal in self.meals_df.iterrows():
                score = 0
                # Match cuisine
                if meal.get('cuisine') in preferences:
                    score += 0.5
                
                # Match vegetarian preference
                if user_profile.get('dietary_restrictions') and 'vegetarian' in user_profile['dietary_restrictions']:
                    if meal.get('is_vegetarian'):
                        score += 0.3
                
                if score > 0:
                    meal_dict = meal.to_dict()
                    meal_dict['similarity_score'] = score
                    meal_dict['explanation'] = self._generate_explanation(meal_dict, user_profile)
                    meal_dict['algorithm'] = 'content_based'
                    recommendations.append(meal_dict)
            
            # Sort by score
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:n]
            
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {str(e)}")
            return []
    
    def _generate_explanation(self, meal, user_profile):
        """Generate human-readable explanation"""
        explanations = []
        
        if meal.get('cuisine') in user_profile.get('favorite_cuisines', []):
            explanations.append(f"Because you love {meal['cuisine']} cuisine")
        
        if meal.get('is_vegetarian') and 'vegetarian' in user_profile.get('dietary_restrictions', []):
            explanations.append("Vegetarian option")
        
        return ' • '.join(explanations) if explanations else "Matches your taste profile"
    
    def get_similar_items(self, meal_id, n=10):
        """Get items similar to a given meal"""
        try:
            if meal_id not in self.meals_df['id'].values:
                return []
            
            # Get the meal
            meal = self.meals_df[self.meals_df['id'] == meal_id].iloc[0]
            cuisine = meal.get('cuisine')
            
            # Find other meals with same cuisine
            similar = self.meals_df[self.meals_df['cuisine'] == cuisine].head(n+1)
            similar = similar[similar['id'] != meal_id].head(n)
            
            return similar.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting similar items: {str(e)}")
            return []


class CollaborativeFiltering:
    """Simplified Collaborative Filtering"""
    
    def __init__(self, ratings_df):
        self.ratings_df = ratings_df
    
    def get_recommendations(self, user_id, meals_df, n=10):
        """Get collaborative filtering recommendations"""
        try:
            # Simplified: return popular items
            if 'rating' in meals_df.columns:
                popular = meals_df.nlargest(n, 'rating')
            else:
                popular = meals_df.head(n)
            
            recommendations = []
            for _, meal in popular.iterrows():
                meal_dict = meal.to_dict()
                meal_dict['predicted_rating'] = meal_dict.get('rating', 4.0)
                meal_dict['explanation'] = "Popular among our users"
                meal_dict['algorithm'] = 'collaborative'
                recommendations.append(meal_dict)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in collaborative recommendations: {str(e)}")
            return []


class ContextualBandit:
    """Simple Contextual Bandit for exploration"""
    
    def __init__(self, n_arms=100, alpha=0.1):
        self.n_arms = n_arms
        self.alpha = alpha
        self.arm_rewards = defaultdict(lambda: {'count': 0, 'sum_rewards': 0})
    
    def select_arms(self, available_arms, user_context, n=5):
        """Select arms using epsilon-greedy strategy"""
        try:
            selected = []
            available = available_arms[:self.n_arms]
            
            # Simple epsilon-greedy: 30% exploration, 70% exploitation
            for arm in available[:n]:
                arm_id = arm['id']
                
                if random.random() < 0.3:  # Explore
                    selected.append(arm)
                else:  # Exploit
                    if arm_id in self.arm_rewards and self.arm_rewards[arm_id]['count'] > 0:
                        # Use existing arms
                        selected.append(arm)
                    else:
                        # New arms for exploration
                        if len(selected) < n:
                            selected.append(arm)
            
            return selected[:n]
            
        except Exception as e:
            logger.error(f"Error in bandit selection: {str(e)}")
            return available_arms[:n]
    
    def update_feedback(self, arm_id, reward, context):
        """Update bandit with feedback"""
        self.arm_rewards[arm_id]['count'] += 1
        self.arm_rewards[arm_id]['sum_rewards'] += reward


class KnowledgeBasedFiltering:
    """Knowledge-based filtering for dietary restrictions"""
    
    def __init__(self, meals_df):
        self.meals_df = meals_df
    
    def filter_by_dietary_restrictions(self, meals, restrictions):
        """Filter meals based on dietary restrictions"""
        if not restrictions:
            return meals
        
        filtered = []
        for meal in meals:
            tags = str(meal.get('tags', '')).lower()
            valid = True
            
            for restriction in restrictions:
                restriction = restriction.lower()
                if restriction == 'vegetarian' and 'non-veg' in tags:
                    valid = False
                    break
                elif restriction == 'vegan' and ('dairy' in tags or 'egg' in tags):
                    valid = False
                    break
                elif restriction == 'gluten-free' and 'gluten' in tags:
                    valid = False
                    break
            
            if valid:
                filtered.append(meal)
        
        return filtered
    
    def filter_by_health_goals(self, meals, health_goals):
        """Filter meals based on health goals"""
        if not health_goals:
            return meals
        
        filtered = []
        for meal in meals:
            valid = True
            
            if health_goals.get('high_protein'):
                if 'protein' not in str(meal.get('name', '')).lower():
                    # Not filtering strictly for demo
                    pass
            
            if valid:
                filtered.append(meal)
        
        return filtered


class RecommendationEngine:
    """Main recommendation engine combining all algorithms"""
    
    def __init__(self, db_path='database/dubbas.db'):
        self.db_path = db_path
        self.meals_df = self._load_meals_data()
        self.ratings_df = self._load_ratings_data()
        
        # Initialize recommenders
        self.content_based = ContentBasedFiltering(self.meals_df)
        self.collaborative = CollaborativeFiltering(self.ratings_df)
        self.knowledge_based = KnowledgeBasedFiltering(self.meals_df)
        self.bandit = ContextualBandit(n_arms=min(len(self.meals_df), 100))
        
        logger.info("Recommendation Engine initialized")
    
    def _load_meals_data(self):
        """Load meals dataset from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM menu_items 
                WHERE is_available = 1
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) > 0:
                logger.info(f"Loaded {len(df)} meals from database")
                return df
            
        except Exception as e:
            logger.error(f"Error loading meals from database: {str(e)}")
        
        # Fallback to sample data
        return self._create_sample_meals()
    
    def _load_ratings_data(self):
        """Load ratings data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT user_id, meal_id, rating 
                FROM user_ratings
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) > 0:
                logger.info(f"Loaded {len(df)} ratings from database")
                return df
            
        except Exception as e:
            logger.error(f"Error loading ratings from database: {str(e)}")
        
        return pd.DataFrame(columns=['user_id', 'meal_id', 'rating'])
    
    def _create_sample_meals(self):
        """Create sample meals for demonstration"""
        data = {
            'id': [f'M00{i}' for i in range(1, 11)],
            'name': [
                'Butter Chicken', 'Paneer Butter Masala', 'Masala Dosa',
                'Vada Pav', 'Hyderabadi Biryani', 'Chole Bhature',
                'Idli Sambar', 'Pav Bhaji', 'Palak Paneer', 'Chicken Biryani'
            ],
            'cuisine': [
                'North Indian', 'North Indian', 'South Indian',
                'Maharashtrian', 'Hyderabadi', 'Punjabi',
                'South Indian', 'Maharashtrian', 'North Indian', 'Hyderabadi'
            ],
            'price': [350, 280, 120, 30, 350, 180, 80, 150, 250, 320],
            'rating': [4.8, 4.7, 4.9, 4.6, 4.8, 4.5, 4.7, 4.6, 4.5, 4.7],
            'is_vegetarian': [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
            'tags': [
                'non-veg,popular', 'veg,popular', 'veg,breakfast',
                'veg,snack', 'non-veg,popular', 'veg,popular',
                'veg,breakfast', 'veg,street food', 'veg,popular', 'non-veg,popular'
            ]
        }
        
        df = pd.DataFrame(data)
        logger.info(f"Created {len(df)} sample meals")
        return df
    
    def get_recommendations(self, user_id, preferences=None, order_history=None, 
                          city='mumbai', time_of_day='any', limit=10):
        """Get personalized recommendations"""
        try:
            # Get candidate meals
            candidates = self._filter_candidates()
            
            if len(candidates) == 0:
                return []
            
            # Get content-based recommendations
            content_recs = self.content_based.get_recommendations(
                preferences or {}, 
                n=limit
            )
            
            # If no content recommendations, use collaborative
            if not content_recs:
                content_recs = self.collaborative.get_recommendations(
                    user_id, 
                    self.meals_df, 
                    n=limit
                )
            
            # Apply knowledge-based filtering
            if preferences:
                content_recs = self.knowledge_based.filter_by_dietary_restrictions(
                    content_recs, 
                    preferences.get('dietary_restrictions', [])
                )
            
            return content_recs[:limit]
            
        except Exception as e:
            logger.error(f"Error in recommendations: {str(e)}")
            return self._get_fallback_recommendations(limit)
    
    def explore_recommendations(self, user_id, preferences=None, history=None, limit=5):
        """Get exploration recommendations"""
        try:
            candidates = self._filter_candidates()
            
            # Simple random exploration
            random.shuffle(candidates)
            selected = candidates[:limit]
            
            for meal in selected:
                meal['explanation'] = "Try something new! We think you might like this"
                meal['algorithm'] = 'exploration'
            
            return selected
            
        except Exception as e:
            logger.error(f"Error in exploration: {str(e)}")
            return []
    
    def get_similar_items(self, meal_id, user_id=None, limit=5):
        """Get items similar to a given meal"""
        try:
            return self.content_based.get_similar_items(meal_id, limit)
        except Exception as e:
            logger.error(f"Error getting similar items: {str(e)}")
            return []
    
    def get_popular_items(self, city=None, limit=10):
        """Get popular items"""
        try:
            candidates = self._filter_candidates()
            
            if 'rating' in self.meals_df.columns:
                candidates.sort(key=lambda x: x.get('rating', 0), reverse=True)
            
            for meal in candidates[:limit]:
                meal['explanation'] = "Popular among our users"
            
            return candidates[:limit]
            
        except Exception as e:
            logger.error(f"Error getting popular items: {str(e)}")
            return []
    
    def get_trending_items(self, city=None, days=7, limit=10):
        """Get trending items"""
        return self.get_popular_items(city, limit)
    
    def record_interaction(self, user_id, meal_id, liked=None, rating=None, context=None):
        """Record user interaction"""
        try:
            # Convert feedback to reward
            if liked is not None:
                reward = 1.0 if liked else 0.0
            elif rating is not None:
                reward = rating / 5.0
            else:
                reward = 0.5
            
            # Update bandit
            self.bandit.update_feedback(meal_id, reward, context or {})
            
            # Save to database
            self._save_interaction(user_id, meal_id, liked, rating, context)
            
        except Exception as e:
            logger.error(f"Error recording interaction: {str(e)}")
    
    def _save_interaction(self, user_id, meal_id, liked, rating, context):
        """Save interaction to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_interactions 
                (id, user_id, meal_id, action, rating, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"INT{random.randint(1000, 9999)}",
                user_id, 
                meal_id,
                'like' if liked else 'dislike' if liked is not None else 'view',
                rating,
                json.dumps(context or {}),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
    
    def _filter_candidates(self, city=None, time_of_day=None):
        """Filter candidate meals"""
        return self.meals_df.to_dict('records')
    
    def _get_fallback_recommendations(self, limit=10):
        """Fallback recommendations"""
        try:
            candidates = self._filter_candidates()
            random.shuffle(candidates)
            for meal in candidates[:limit]:
                meal['explanation'] = "Recommended for you"
            return candidates[:limit]
        except:
            return []