// Translation Manager for Multi-Language Support

class TranslationManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.supportedLanguages = [
            'en', 'hi', 'mr', 'ta', 'te', 'kn', 'ml', 
            'bn', 'gu', 'pa', 'or', 'as', 'ur'
        ];
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.rtlLanguages = ['ur'];
        this.initialized = false;
        this.loadingPromises = {};
    }

    async init() {
        if (this.initialized) return;
        
        await this.loadLanguage(this.currentLanguage);
        this.setupLanguageSelector();
        this.applyLanguageDirection();
        this.initialized = true;
        
        // Listen for language changes
        document.addEventListener('languageChanged', (e) => {
            this.currentLanguage = e.detail.language;
            this.updatePageContent();
        });
        
        console.log(`✅ Translation Manager initialized with language: ${this.currentLanguage}`);
    }

    async loadLanguage(langCode) {
        if (!this.supportedLanguages.includes(langCode)) {
            langCode = this.fallbackLanguage;
        }
        
        // Prevent multiple simultaneous loads
        if (this.loadingPromises[langCode]) {
            return this.loadingPromises[langCode];
        }
        
        this.loadingPromises[langCode] = this._loadLanguageFiles(langCode);
        
        try {
            await this.loadingPromises[langCode];
            return true;
        } catch (error) {
            console.error(`❌ Failed to load translations for ${langCode}:`, error);
            
            if (langCode !== this.fallbackLanguage) {
                return this.loadLanguage(this.fallbackLanguage);
            }
            return false;
        } finally {
            delete this.loadingPromises[langCode];
        }
    }

    async _loadLanguageFiles(langCode) {
        // Load all translation files for this language
        const [common, customer, provider, owner] = await Promise.all([
            this.loadTranslationFile(langCode, 'common'),
            this.loadTranslationFile(langCode, 'customer'),
            this.loadTranslationFile(langCode, 'provider'),
            this.loadTranslationFile(langCode, 'owner')
        ]);
        
        this.translations[langCode] = {
            ...common,
            ...customer,
            ...provider,
            ...owner
        };
        
        console.log(`✅ Loaded translations for ${langCode}`);
    }

    async loadTranslationFile(langCode, domain) {
        try {
            // Try to load from locales folder
            const response = await fetch(`/locales/${langCode}/${domain}.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.warn(`Could not load ${domain}.json for ${langCode}, using fallback`);
            
            // Return empty object as fallback
            return {};
        }
    }

    translate(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                // Try fallback language
                return this.translateFromFallback(key, params);
            }
        }
        
        if (typeof value === 'string') {
            return this.replaceParams(value, params);
        }
        
        return key;
    }

    translateFromFallback(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.fallbackLanguage];
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return key;
            }
        }
        
        if (typeof value === 'string') {
            return this.replaceParams(value, params);
        }
        
        return key;
    }

    replaceParams(text, params) {
        return text.replace(/{(\w+)}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }

    applyLanguageDirection() {
        const isRTL = this.rtlLanguages.includes(this.currentLanguage);
        document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
        document.documentElement.lang = this.currentLanguage;
        
        // Load RTL CSS if needed
        if (isRTL) {
            this.loadRTLCSS();
        } else {
            this.removeRTLCSS();
        }
    }

    loadRTLCSS() {
        if (!document.querySelector('#rtl-css')) {
            const link = document.createElement('link');
            link.id = 'rtl-css';
            link.rel = 'stylesheet';
            link.href = '/frontend/assets/css/rtl.css';
            document.head.appendChild(link);
        }
    }

    removeRTLCSS() {
        const rtlCSS = document.querySelector('#rtl-css');
        if (rtlCSS) {
            rtlCSS.remove();
        }
    }

    setupLanguageSelector() {
        const selector = document.querySelector('.language-selector');
        if (!selector) return;
        
        const langBtn = selector.querySelector('.lang-btn');
        const dropdown = selector.querySelector('.lang-dropdown');
        
        if (!langBtn || !dropdown) return;
        
        // Update button text
        const langName = this.getLanguageName(this.currentLanguage);
        langBtn.innerHTML = `<i class="fas fa-globe"></i> <span>${langName}</span> <i class="fas fa-chevron-down"></i>`;
        
        // Clear dropdown
        dropdown.innerHTML = '';
        
        // Add language options
        this.supportedLanguages.forEach(code => {
            const name = this.getLanguageName(code);
            const nativeName = this.getNativeLanguageName(code);
            const isActive = code === this.currentLanguage;
            
            const link = document.createElement('a');
            link.href = '#';
            link.dataset.lang = code;
            link.className = isActive ? 'active' : '';
            link.innerHTML = `${this.getLanguageFlag(code)} ${nativeName} (${name})`;
            
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.switchLanguage(code);
            });
            
            dropdown.appendChild(link);
        });
    }

    async switchLanguage(langCode) {
        if (langCode === this.currentLanguage) return;
        
        const success = await this.loadLanguage(langCode);
        if (success) {
            this.currentLanguage = langCode;
            localStorage.setItem('language', langCode);
            this.applyLanguageDirection();
            this.updatePageContent();
            this.setupLanguageSelector();
            
            // Dispatch event
            document.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language: langCode }
            }));
            
            // Show success message
            if (window.showAlert) {
                window.showAlert(`Language changed to ${this.getLanguageName(langCode)}`, 'success');
            }
        }
    }

    updatePageContent() {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            const translation = this.translate(key);
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.type === 'placeholder' || element.placeholder) {
                    element.placeholder = translation;
                } else {
                    element.value = translation;
                }
            } else {
                element.textContent = translation;
            }
        });
        
        // Update placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.dataset.i18nPlaceholder;
            element.placeholder = this.translate(key);
        });
        
        // Update titles
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.dataset.i18nTitle;
            element.title = this.translate(key);
        });
        
        // Update alt text
        document.querySelectorAll('[data-i18n-alt]').forEach(element => {
            const key = element.dataset.i18nAlt;
            element.alt = this.translate(key);
        });
        
        // Update aria labels
        document.querySelectorAll('[data-i18n-aria]').forEach(element => {
            const key = element.dataset.i18nAria;
            element.setAttribute('aria-label', this.translate(key));
        });
    }

    getLanguageName(code) {
        const names = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'ur': 'Urdu'
        };
        return names[code] || code;
    }

    getNativeLanguageName(code) {
        const names = {
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
        };
        return names[code] || code;
    }

    getLanguageFlag(code) {
        const flags = {
            'en': '🇬🇧',
            'hi': '🇮🇳',
            'mr': '🇮🇳',
            'ta': '🇮🇳',
            'te': '🇮🇳',
            'kn': '🇮🇳',
            'ml': '🇮🇳',
            'bn': '🇮🇳',
            'gu': '🇮🇳',
            'pa': '🇮🇳',
            'or': '🇮🇳',
            'as': '🇮🇳',
            'ur': '🇮🇳'
        };
        return flags[code] || '🌐';
    }

    formatNumber(number, options = {}) {
        try {
            return new Intl.NumberFormat(this.currentLanguage, options).format(number);
        } catch (e) {
            return number.toString();
        }
    }

    formatCurrency(amount, currency = 'INR') {
        try {
            return new Intl.NumberFormat(this.currentLanguage, {
                style: 'currency',
                currency: currency,
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount);
        } catch (e) {
            return `₹${amount}`;
        }
    }

    formatDate(date, options = {}) {
        try {
            const defaultOptions = {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            };
            return new Intl.DateTimeFormat(this.currentLanguage, {
                ...defaultOptions,
                ...options
            }).format(new Date(date));
        } catch (e) {
            return new Date(date).toLocaleDateString();
        }
    }

    formatTime(date) {
        try {
            return new Intl.DateTimeFormat(this.currentLanguage, {
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date(date));
        } catch (e) {
            return new Date(date).toLocaleTimeString();
        }
    }

    formatDateTime(date) {
        try {
            return new Intl.DateTimeFormat(this.currentLanguage, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }).format(new Date(date));
        } catch (e) {
            return new Date(date).toLocaleString();
        }
    }

    formatRelativeTime(date) {
        try {
            const rtf = new Intl.RelativeTimeFormat(this.currentLanguage, { numeric: 'auto' });
            const now = new Date();
            const then = new Date(date);
            const diffInSeconds = (then - now) / 1000;
            
            if (Math.abs(diffInSeconds) < 60) {
                return rtf.format(Math.round(diffInSeconds), 'second');
            }
            
            const diffInMinutes = diffInSeconds / 60;
            if (Math.abs(diffInMinutes) < 60) {
                return rtf.format(Math.round(diffInMinutes), 'minute');
            }
            
            const diffInHours = diffInMinutes / 60;
            if (Math.abs(diffInHours) < 24) {
                return rtf.format(Math.round(diffInHours), 'hour');
            }
            
            const diffInDays = diffInHours / 24;
            if (Math.abs(diffInDays) < 30) {
                return rtf.format(Math.round(diffInDays), 'day');
            }
            
            const diffInMonths = diffInDays / 30;
            if (Math.abs(diffInMonths) < 12) {
                return rtf.format(Math.round(diffInMonths), 'month');
            }
            
            const diffInYears = diffInMonths / 12;
            return rtf.format(Math.round(diffInYears), 'year');
        } catch (e) {
            return this.formatDate(date);
        }
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }

    getSupportedLanguages() {
        return this.supportedLanguages.map(code => ({
            code: code,
            name: this.getLanguageName(code),
            nativeName: this.getNativeLanguageName(code),
            flag: this.getLanguageFlag(code),
            isRTL: this.rtlLanguages.includes(code)
        }));
    }

    isRTL() {
        return this.rtlLanguages.includes(this.currentLanguage);
    }
}

// Initialize translation manager
const i18n = new TranslationManager();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});

// Make it globally available
window.i18n = i18n;
window.t = (key, params) => i18n.translate(key, params);

// Helper function for translations in HTML
function __(key, params) {
    return i18n.translate(key, params);
}