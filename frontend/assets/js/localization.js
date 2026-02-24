// Localization and Regional Content JavaScript

// Regional content manager
class RegionalManager {
    constructor() {
        this.currentCity = localStorage.getItem('city') || 'mumbai';
        this.cities = {
            'mumbai': {
                name: 'Mumbai',
                state: 'Maharashtra',
                language: 'mr',
                localDishes: ['Vada Pav', 'Pav Bhaji', 'Misal Pav', 'Puran Poli', 'Modak'],
                festivals: ['Ganesh Chaturthi', 'Gudi Padwa'],
                popularAreas: ['Andheri', 'Bandra', 'Dadar', 'Juhu', 'Colaba']
            },
            'delhi': {
                name: 'Delhi',
                state: 'Delhi',
                language: 'hi',
                localDishes: ['Chole Bhature', 'Paratha', 'Butter Chicken', 'Aloo Tikki'],
                festivals: ['Diwali', 'Dussehra', 'Holi'],
                popularAreas: ['Connaught Place', 'Chandni Chowk', 'South Delhi', 'North Delhi']
            },
            'bangalore': {
                name: 'Bangalore',
                state: 'Karnataka',
                language: 'kn',
                localDishes: ['Bisi Bele Bath', 'Mysore Pak', 'Dosa', 'Idli', 'Filter Coffee'],
                festivals: ['Ugadi', 'Karaga'],
                popularAreas: ['Indiranagar', 'Koramangala', 'Whitefield', 'MG Road']
            },
            'chennai': {
                name: 'Chennai',
                state: 'Tamil Nadu',
                language: 'ta',
                localDishes: ['Idli', 'Dosa', 'Sambar', 'Pongal', 'Filter Coffee'],
                festivals: ['Pongal', 'Tamil New Year'],
                popularAreas: ['T Nagar', 'Anna Nagar', 'Adyar', 'Velachery']
            },
            'kolkata': {
                name: 'Kolkata',
                state: 'West Bengal',
                language: 'bn',
                localDishes: ['Macher Jhol', 'Roshogolla', 'Sandesh', 'Kathi Roll'],
                festivals: ['Durga Puja', 'Kali Puja'],
                popularAreas: ['Salt Lake', 'New Town', 'Park Street', 'Howrah']
            },
            'hyderabad': {
                name: 'Hyderabad',
                state: 'Telangana',
                language: 'te',
                localDishes: ['Hyderabadi Biryani', 'Haleem', 'Kebabs', 'Double Ka Meetha'],
                festivals: ['Eid', 'Diwali'],
                popularAreas: ['Banjara Hills', 'Jubilee Hills', 'Gachibowli', 'Hitech City']
            },
            'pune': {
                name: 'Pune',
                state: 'Maharashtra',
                language: 'mr',
                localDishes: ['Misal Pav', 'Pithla Bhakri', 'Puri Bhaji', 'Sabudana Khichdi'],
                festivals: ['Ganesh Chaturthi', 'Gudi Padwa'],
                popularAreas: ['Koregaon Park', 'Viman Nagar', 'Hinjewadi', 'Kothrud']
            },
            'ahmedabad': {
                name: 'Ahmedabad',
                state: 'Gujarat',
                language: 'gu',
                localDishes: ['Dhokla', 'Khandvi', 'Thepla', 'Undhiyu'],
                festivals: ['Navratri', 'Uttarayan'],
                popularAreas: ['Navrangpura', 'Satellite', 'SG Highway', 'Vastrapur']
            },
            'jaipur': {
                name: 'Jaipur',
                state: 'Rajasthan',
                language: 'hi',
                localDishes: ['Dal Baati Churma', 'Gatte ki Sabzi', 'Laal Maas', 'Pyaz Kachori'],
                festivals: ['Teej', 'Gangaur'],
                popularAreas: ['C Scheme', 'Vaishali Nagar', 'Malviya Nagar', 'Mansarovar']
            },
            'lucknow': {
                name: 'Lucknow',
                state: 'Uttar Pradesh',
                language: 'hi',
                localDishes: ['Galouti Kebab', 'Biryani', 'Nihari', 'Sheermal'],
                festivals: ['Eid', 'Diwali'],
                popularAreas: ['Hazratganj', 'Gomti Nagar', 'Alambagh', 'Chowk']
            }
        };
    }

    // Get current city info
    getCurrentCity() {
        return this.cities[this.currentCity] || this.cities['mumbai'];
    }

    // Change city
    setCity(city) {
        if (this.cities[city]) {
            this.currentCity = city;
            localStorage.setItem('city', city);
            
            // Also change language to match city
            const language = this.cities[city].language;
            if (window.i18n) {
                window.i18n.switchLanguage(language);
            }
            
            // Dispatch city change event
            document.dispatchEvent(new CustomEvent('cityChanged', {
                detail: { city: city, cityInfo: this.cities[city] }
            }));
            
            return true;
        }
        return false;
    }

    // Get all cities
    getAllCities() {
        return Object.entries(this.cities).map(([id, info]) => ({
            id: id,
            name: info.name,
            state: info.state,
            language: info.language
        }));
    }

    // Get popular cities
    getPopularCities(limit = 6) {
        const popular = ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad'];
        return popular.slice(0, limit).map(id => ({
            id: id,
            name: this.cities[id].name,
            language: this.cities[id].language
        }));
    }

    // Get local dishes for current city
    getLocalDishes() {
        return this.getCurrentCity().localDishes;
    }

    // Get festivals for current city
    getCurrentFestivals() {
        const currentMonth = new Date().getMonth() + 1;
        const city = this.getCurrentCity();
        
        // Map months to festivals (simplified)
        const festivalMap = {
            'mumbai': { 8: 'Ganesh Chaturthi', 3: 'Gudi Padwa' },
            'delhi': { 10: 'Diwali', 3: 'Holi' },
            'chennai': { 1: 'Pongal', 4: 'Tamil New Year' },
            'kolkata': { 10: 'Durga Puja' },
            'ahmedabad': { 10: 'Navratri' }
        };
        
        const cityFestivals = festivalMap[this.currentCity] || {};
        return cityFestivals[currentMonth] || null;
    }

    // Get greeting in local language
    getLocalGreeting() {
        const hour = new Date().getHours();
        const city = this.getCurrentCity();
        
        const greetings = {
            'mr': {
                morning: 'सुप्रभात',
                afternoon: 'शुभ दुपार',
                evening: 'शुभ संध्याकाळ',
                night: 'शुभ रात्री'
            },
            'hi': {
                morning: 'सुप्रभात',
                afternoon: 'नमस्ते',
                evening: 'शुभ संध्या',
                night: 'शुभ रात्रि'
            },
            'ta': {
                morning: 'காலை வணக்கம்',
                afternoon: 'மதிய வணக்கம்',
                evening: 'மாலை வணக்கம்',
                night: 'இரவு வணக்கம்'
            },
            'te': {
                morning: 'శుభోదయం',
                afternoon: 'శుభ మధ్యాహ్నం',
                evening: 'శుభ సాయంత్రం',
                night: 'శుభ రాత్రి'
            },
            'kn': {
                morning: 'ಶುಭೋದಯ',
                afternoon: 'ಶುಭ ಮಧ್ಯಾಹ್ನ',
                evening: 'ಶುಭ ಸಂಜೆ',
                night: 'ಶುಭ ರಾತ್ರಿ'
            },
            'ml': {
                morning: 'സുപ്രഭാതം',
                afternoon: 'ഗുഡ് ആഫ്റ്റർനൂൺ',
                evening: 'ഗുഡ് ഈവനിംഗ്',
                night: 'ശുഭ രാത്രി'
            },
            'bn': {
                morning: 'সুপ্রভাত',
                afternoon: 'শুভ অপরাহ্ন',
                evening: 'শুভ সন্ধ্যা',
                night: 'শুভ রাত্রি'
            },
            'gu': {
                morning: 'સુપ્રભાત',
                afternoon: 'શુભ બપોર',
                evening: 'શુભ સાંજ',
                night: 'શુભ રાત્રિ'
            },
            'pa': {
                morning: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ',
                afternoon: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ',
                evening: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ',
                night: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ'
            }
        };
        
        const langGreetings = greetings[city.language] || greetings['hi'];
        
        if (hour < 12) return langGreetings.morning;
        if (hour < 17) return langGreetings.afternoon;
        if (hour < 20) return langGreetings.evening;
        return langGreetings.night;
    }

    // Get delivery estimate based on city and area
    getDeliveryEstimate(area) {
        const baseTime = 30; // minutes
        const city = this.getCurrentCity();
        
        // Add time based on area distance (simplified)
        const areaIndex = city.popularAreas.indexOf(area);
        const additionalTime = areaIndex >= 0 ? areaIndex * 5 : 15;
        
        return {
            min: baseTime + additionalTime - 5,
            max: baseTime + additionalTime + 5,
            unit: 'minutes'
        };
    }

    // Check if today is a festival in current city
    isFestivalToday() {
        const festival = this.getCurrentFestivals();
        return festival ? {
            name: festival,
            special: true,
            message: `Special ${festival} dishes available!`
        } : null;
    }
}

// Initialize regional manager
const regionalManager = new RegionalManager();

// City selector functionality
function initCitySelector() {
    const cityBtns = document.querySelectorAll('.city-btn');
    if (!cityBtns.length) return;
    
    // Set active city from localStorage
    const currentCity = localStorage.getItem('city') || 'mumbai';
    cityBtns.forEach(btn => {
        if (btn.dataset.city === currentCity) {
            btn.classList.add('active');
        }
        
        btn.addEventListener('click', function() {
            const city = this.dataset.city;
            regionalManager.setCity(city);
            
            // Update active state
            cityBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Reload city-specific content
            loadCityContent(city);
        });
    });
}

// Load city-specific content
async function loadCityContent(city) {
    // Update local dishes
    const dishesContainer = document.getElementById('localDishes');
    if (dishesContainer) {
        const dishes = regionalManager.getLocalDishes();
        dishesContainer.innerHTML = dishes.map(dish => `
            <span class="dish-tag">${dish}</span>
        `).join('');
    }
    
    // Update greeting
    const greetingEl = document.getElementById('cityGreeting');
    if (greetingEl) {
        greetingEl.textContent = regionalManager.getLocalGreeting();
    }
    
    // Check for festivals
    const festival = regionalManager.isFestivalToday();
    const festivalBanner = document.getElementById('festivalBanner');
    if (festivalBanner && festival) {
        festivalBanner.innerHTML = `
            <div class="festival-alert">
                <i class="fas fa-gift"></i>
                ${festival.message}
            </div>
        `;
        festivalBanner.style.display = 'block';
    }
    
    // Load city-specific recommendations
    if (window.loadRecommendations) {
        window.loadRecommendations();
    }
    
    // Dispatch event for other components
    document.dispatchEvent(new CustomEvent('cityContentLoaded', {
        detail: { city: city }
    }));
}

// Get user's location
function detectUserLocation() {
    if (!navigator.geolocation) {
        console.warn('Geolocation not supported');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
            
            try {
                // Reverse geocode to get city
                const response = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
                );
                const data = await response.json();
                
                if (data.address && data.address.city) {
                    const detectedCity = data.address.city.toLowerCase();
                    
                    // Check if city is supported
                    if (regionalManager.cities[detectedCity]) {
                        regionalManager.setCity(detectedCity);
                        
                        // Update UI
                        const cityBtns = document.querySelectorAll('.city-btn');
                        cityBtns.forEach(btn => {
                            if (btn.dataset.city === detectedCity) {
                                btn.classList.add('active');
                            } else {
                                btn.classList.remove('active');
                            }
                        });
                        
                        loadCityContent(detectedCity);
                        showAlert(`Location detected: ${regionalManager.cities[detectedCity].name}`, 'success');
                    }
                }
            } catch (error) {
                console.error('Error detecting location:', error);
            }
        },
        (error) => {
            console.warn('Location detection failed:', error);
        }
    );
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initCitySelector();
    
    // Auto-detect location if enabled
    if (localStorage.getItem('autoDetectLocation') === 'true') {
        detectUserLocation();
    }
    
    // Location detect button
    const locationBtn = document.getElementById('detectLocation');
    if (locationBtn) {
        locationBtn.addEventListener('click', detectUserLocation);
    }
});

// Export for use in other scripts
window.regionalManager = regionalManager;
window.detectUserLocation = detectUserLocation;