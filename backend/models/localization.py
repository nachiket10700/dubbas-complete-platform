"""
Localization Module - Supports 13 Indian Languages
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class TranslationManager:
    """Handle translations for multiple languages"""
    
    def __init__(self):
        self.supported_languages = ['en', 'hi', 'mr', 'ta', 'te', 'kn', 'ml', 'bn', 'gu', 'pa', 'or', 'as', 'ur']
        self.default_language = 'en'
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict:
        """Load translation dictionaries"""
        return {
            'en': {
                'welcome': 'Welcome to DUBBA\'s',
                'login': 'Login',
                'signup': 'Sign Up',
                'home': 'Home',
                'menu': 'Menu',
                'orders': 'Orders',
                'profile': 'Profile',
                'subscriptions': 'Subscriptions',
                'payments': 'Payments',
                'complaints': 'Complaints',
                'breakfast': 'Breakfast',
                'lunch': 'Lunch',
                'dinner': 'Dinner',
                'snacks': 'Snacks',
                'add_to_cart': 'Add to Cart',
                'checkout': 'Checkout',
                'total': 'Total',
                'recommendations': 'Recommendations',
                'regional_special': 'Special from {region}'
            },
            'hi': {
                'welcome': 'डब्बा में आपका स्वागत है',
                'login': 'लॉग इन',
                'signup': 'साइन अप',
                'home': 'होम',
                'menu': 'मेनू',
                'orders': 'ऑर्डर',
                'profile': 'प्रोफाइल',
                'subscriptions': 'सदस्यता',
                'payments': 'भुगतान',
                'complaints': 'शिकायत',
                'breakfast': 'नाश्ता',
                'lunch': 'दोपहर का भोजन',
                'dinner': 'रात का खाना',
                'snacks': 'नाश्ता',
                'add_to_cart': 'कार्ट में डालें',
                'checkout': 'चेकआउट',
                'total': 'कुल',
                'recommendations': 'सिफारिशें',
                'regional_special': '{region} से विशेष'
            },
            'mr': {
                'welcome': 'डब्बामध्ये आपले स्वागत आहे',
                'login': 'लॉगिन',
                'signup': 'साइन अप',
                'home': 'मुख्यपृष्ठ',
                'menu': 'मेनू',
                'orders': 'ऑर्डर',
                'profile': 'प्रोफाइल',
                'subscriptions': 'सदस्यता',
                'payments': 'पेमेंट',
                'complaints': 'तक्रारी',
                'breakfast': 'नाश्ता',
                'lunch': 'दुपारचे जेवण',
                'dinner': 'रात्रीचे जेवण',
                'snacks': 'स्नॅक्स',
                'add_to_cart': 'कार्टमध्ये घाला',
                'checkout': 'चेकआउट',
                'total': 'एकूण',
                'recommendations': 'शिफारसी',
                'regional_special': '{region} मधील विशेष'
            },
            'ta': {
                'welcome': 'டப்பாவிற்கு வரவேற்கிறோம்',
                'login': 'உள்நுழைய',
                'signup': 'பதிவு செய்க',
                'home': 'முகப்பு',
                'menu': 'மெனு',
                'orders': 'ஆர்டர்கள்',
                'profile': 'சுயவிவரம்',
                'subscriptions': 'சந்தாக்கள்',
                'payments': 'கட்டணங்கள்',
                'complaints': 'புகார்கள்',
                'breakfast': 'காலை உணவு',
                'lunch': 'மதிய உணவு',
                'dinner': 'இரவு உணவு',
                'snacks': 'சிற்றுண்டி',
                'add_to_cart': 'வண்டியில் சேர்க்கவும்',
                'checkout': 'செலுத்தவும்',
                'total': 'மொத்தம்',
                'recommendations': 'பரிந்துரைகள்',
                'regional_special': '{region} இலிருந்து சிறப்பு'
            },
            'te': {
                'welcome': 'డబ్బాకు స్వాగతం',
                'login': 'లాగిన్',
                'signup': 'సైన్ అప్',
                'home': 'హోమ్',
                'menu': 'మెనూ',
                'orders': 'ఆర్డర్లు',
                'profile': 'ప్రొఫైల్',
                'subscriptions': 'సభ్యత్వాలు',
                'payments': 'చెల్లింపులు',
                'complaints': 'ఫిర్యాదులు',
                'breakfast': 'అల్పాహారం',
                'lunch': 'మధ్యాహ్న భోజనం',
                'dinner': 'రాత్రి భోజనం',
                'snacks': 'చిరుతిండి',
                'add_to_cart': 'కార్ట్‌లో చేర్చండి',
                'checkout': 'చెక్అవుట్',
                'total': 'మొత్తం',
                'recommendations': 'సిఫార్సులు',
                'regional_special': '{region} నుండి ప్రత్యేక'
            },
            'kn': {
                'welcome': 'ಡಬ್ಬಾಗೆ ಸ್ವಾಗತ',
                'login': 'ಲಾಗಿನ್',
                'signup': 'ಸೈನ್ ಅಪ್',
                'home': 'ಮುಖಪುಟ',
                'menu': 'ಮೆನು',
                'orders': 'ಆರ್ಡರ್‌ಗಳು',
                'profile': 'ಪ್ರೊಫೈಲ್',
                'subscriptions': 'ಚಂದಾದಾರಿಕೆಗಳು',
                'payments': 'ಪಾವತಿಗಳು',
                'complaints': 'ದೂರುಗಳು',
                'breakfast': 'ತಿಂಡಿ',
                'lunch': 'ಮಧ್ಯಾಹ್ನದ ಊಟ',
                'dinner': 'ರಾತ್ರಿ ಊಟ',
                'snacks': 'ಉಪಹಾರ',
                'add_to_cart': 'ಕಾರ್ಟ್‌ಗೆ ಸೇರಿಸಿ',
                'checkout': 'ಚೆಕ್‌ಔಟ್',
                'total': 'ಒಟ್ಟು',
                'recommendations': 'ಶಿಫಾರಸುಗಳು',
                'regional_special': '{region} ನಿಂದ ವಿಶೇಷ'
            },
            'ml': {
                'welcome': 'ഡബ്ബയിലേക്ക് സ്വാഗതം',
                'login': 'ലോഗിൻ',
                'signup': 'സൈൻ അപ്പ്',
                'home': 'ഹോം',
                'menu': 'മെനു',
                'orders': 'ഓർഡറുകൾ',
                'profile': 'പ്രൊഫൈൽ',
                'subscriptions': 'സബ്‌സ്ക്രിപ്‌ഷനുകൾ',
                'payments': 'പേയ്‌മെന്റുകൾ',
                'complaints': 'പരാതികൾ',
                'breakfast': 'പ്രഭാത ഭക്ഷണം',
                'lunch': 'ഉച്ചഭക്ഷണം',
                'dinner': 'രാത്രി ഭക്ഷണം',
                'snacks': 'ലഘുഭക്ഷണം',
                'add_to_cart': 'കാർട്ടിലേക്ക് ചേർക്കുക',
                'checkout': 'ചെക്ക്‌ഔട്ട്',
                'total': 'ആകെ',
                'recommendations': 'ശുപാർശകൾ',
                'regional_special': '{region} ൽ നിന്നുള്ള പ്രത്യേകത'
            }
        }
    
    def get_available_languages(self) -> List[Dict]:
        """Get list of available languages"""
        language_names = {
            'en': 'English',
            'hi': 'हिन्दी',
            'mr': 'मराठी',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'kn': 'ಕನ್ನಡ',
            'ml': 'മലയാളം',
            'bn': 'বাংলা',
            'gu': 'ગુજરાતી',
            'pa': 'ਪੰਜਾਬੀ',
            'or': 'ଓଡ଼ିଆ',
            'as': 'অসমীয়া',
            'ur': 'اردو'
        }
        
        return [{
            'code': lang,
            'name': language_names.get(lang, lang),
            'is_rtl': lang == 'ur'
        } for lang in self.supported_languages]
    
    def translate(self, key: str, language: str = 'en', **kwargs) -> str:
        """Translate a key to the specified language"""
        if language not in self.supported_languages:
            language = self.default_language
        
        translation = self.translations.get(language, {}).get(key, key)
        
        # Replace placeholders
        if kwargs:
            for k, v in kwargs.items():
                translation = translation.replace(f'{{{k}}}', str(v))
        
        return translation


class RegionalContentManager:
    """Manage region-specific content, festivals, and local specialties"""
    
    def __init__(self):
        self.regions = {
            'maharashtra': {
                'language': 'mr',
                'capital': 'mumbai',
                'festivals': [
                    {'name': 'Ganesh Chaturthi', 'month': 8, 'duration_days': 10},
                    {'name': 'Gudi Padwa', 'month': 3, 'duration_days': 1},
                    {'name': 'Diwali', 'month': 10, 'duration_days': 5}
                ],
                'local_dishes': [
                    'Vada Pav', 'Pav Bhaji', 'Misal Pav', 'Puran Poli',
                    'Modak', 'Sabudana Khichdi', 'Bombil Fry'
                ],
                'famous_areas': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Kolhapur']
            },
            'tamilnadu': {
                'language': 'ta',
                'capital': 'chennai',
                'festivals': [
                    {'name': 'Pongal', 'month': 1, 'duration_days': 4},
                    {'name': 'Tamil New Year', 'month': 4, 'duration_days': 1},
                    {'name': 'Diwali', 'month': 10, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Idli', 'Dosa', 'Sambar', 'Vada', 'Pongal',
                    'Chettinad Chicken', 'Filter Coffee', 'Kothu Parotta'
                ],
                'famous_areas': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy', 'Salem']
            },
            'andhrapradesh': {
                'language': 'te',
                'capital': 'amaravati',
                'festivals': [
                    {'name': 'Ugadi', 'month': 3, 'duration_days': 1},
                    {'name': 'Sankranthi', 'month': 1, 'duration_days': 3},
                    {'name': 'Diwali', 'month': 10, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Hyderabadi Biryani', 'Gongura Pickle', 'Pesarattu',
                    'Pulihora', 'Gutti Vankaya', 'Bobbatlu'
                ],
                'famous_areas': ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Tirupati']
            },
            'karnataka': {
                'language': 'kn',
                'capital': 'bangalore',
                'festivals': [
                    {'name': 'Ugadi', 'month': 3, 'duration_days': 1},
                    {'name': 'Karaga', 'month': 4, 'duration_days': 1},
                    {'name': 'Diwali', 'month': 10, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Bisi Bele Bath', 'Mysore Pak', 'Dosa', 'Idli',
                    'Neer Dosa', 'Kori Rotti', 'Mangalore Bajji'
                ],
                'famous_areas': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum']
            },
            'kerala': {
                'language': 'ml',
                'capital': 'thiruvananthapuram',
                'festivals': [
                    {'name': 'Onam', 'month': 8, 'duration_days': 10},
                    {'name': 'Vishu', 'month': 4, 'duration_days': 1},
                    {'name': 'Christmas', 'month': 12, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Appam with Stew', 'Puttu and Kadala Curry', 'Sadya',
                    'Malabar Biryani', 'Karimeen Pollichathu', 'Payasam'
                ],
                'famous_areas': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur']
            },
            'westbengal': {
                'language': 'bn',
                'capital': 'kolkata',
                'festivals': [
                    {'name': 'Durga Puja', 'month': 10, 'duration_days': 5},
                    {'name': 'Kali Puja', 'month': 10, 'duration_days': 1},
                    {'name': 'Poila Boishakh', 'month': 4, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Macher Jhol', 'Shorshe Ilish', 'Chingri Malai Curry',
                    'Aloo Posto', 'Roshogolla', 'Sandesh', 'Mishti Doi'
                ],
                'famous_areas': ['Kolkata', 'Howrah', 'Durgapur', 'Siliguri']
            },
            'gujarat': {
                'language': 'gu',
                'capital': 'gandhinagar',
                'festivals': [
                    {'name': 'Navratri', 'month': 10, 'duration_days': 9},
                    {'name': 'Diwali', 'month': 10, 'duration_days': 5},
                    {'name': 'Uttarayan', 'month': 1, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Dhokla', 'Khandvi', 'Thepla', 'Undhiyu',
                    'Fafda-Jalebi', 'Handvo', 'Mohanthal'
                ],
                'famous_areas': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot']
            },
            'punjab': {
                'language': 'pa',
                'capital': 'chandigarh',
                'festivals': [
                    {'name': 'Lohri', 'month': 1, 'duration_days': 1},
                    {'name': 'Baisakhi', 'month': 4, 'duration_days': 1},
                    {'name': 'Gurpurab', 'month': 11, 'duration_days': 1}
                ],
                'local_dishes': [
                    'Butter Chicken', 'Sarson ka Saag', 'Makki di Roti',
                    'Chole Bhature', 'Amritsari Fish', 'Lassi'
                ],
                'famous_areas': ['Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala']
            }
        }
        
        self.city_to_region = {
            'mumbai': 'maharashtra', 'pune': 'maharashtra', 'nagpur': 'maharashtra',
            'chennai': 'tamilnadu', 'coimbatore': 'tamilnadu', 'madurai': 'tamilnadu',
            'hyderabad': 'andhrapradesh', 'visakhapatnam': 'andhrapradesh',
            'bangalore': 'karnataka', 'mysore': 'karnataka', 'mangalore': 'karnataka',
            'kochi': 'kerala', 'thiruvananthapuram': 'kerala', 'kozhikode': 'kerala',
            'kolkata': 'westbengal', 'howrah': 'westbengal', 'siliguri': 'westbengal',
            'ahmedabad': 'gujarat', 'surat': 'gujarat', 'vadodara': 'gujarat',
            'amritsar': 'punjab', 'ludhiana': 'punjab', 'chandigarh': 'punjab',
            'delhi': 'delhi', 'jaipur': 'rajasthan', 'lucknow': 'uttarpradesh'
        }
    
    def get_region_info(self, city: str) -> Dict:
        """Get region information based on city"""
        city_lower = city.lower()
        region_key = self.city_to_region.get(city_lower, 'maharashtra')
        return self.regions.get(region_key, self.regions['maharashtra'])
    
    def get_festive_special(self, region_language: str) -> Optional[Dict]:
        """Get festive special information"""
        # Simplified for now
        current_month = datetime.now().month
        
        for region, info in self.regions.items():
            if info['language'] == region_language:
                for festival in info['festivals']:
                    if festival['month'] == current_month:
                        return {
                            'name': festival['name'],
                            'is_ongoing': True,
                            'special_message': f"Special {festival['name']} dishes available!"
                        }
        
        return None
    
    def get_local_recommendations(self, city: str, time_of_day: str = 'any') -> List[Dict]:
        """Get local food recommendations based on city and time"""
        region = self.get_region_info(city)
        language = region['language']
        
        time_based = {
            'breakfast': ['Idli', 'Dosa', 'Poha', 'Upma', 'Paratha'],
            'lunch': ['Thali', 'Biryani', 'Curry Rice', 'Dal Rice'],
            'dinner': ['Thali', 'Roti Sabzi', 'Biryani', 'Fried Rice'],
            'snack': ['Samosa', 'Vada Pav', 'Pani Puri', 'Bhel Puri']
        }
        
        # Combine local dishes with time-based recommendations
        local_dishes = region['local_dishes']
        time_dishes = time_based.get(time_of_day, [])
        
        # Find matching dishes
        recommendations = []
        for dish in local_dishes[:5]:
            recommendations.append({
                'name': dish,
                'language': language,
                'region': region['capital'],
                'description': f"Popular {region['capital']} {time_of_day} dish"
            })
        
        return recommendations
    
    def get_cities(self) -> List[str]:
        """Get list of supported cities"""
        return list(set(self.city_to_region.keys()))
    
    def get_areas(self, city: str) -> List[str]:
        """Get areas in a city"""
        region = self.get_region_info(city)
        return region.get('famous_areas', [])