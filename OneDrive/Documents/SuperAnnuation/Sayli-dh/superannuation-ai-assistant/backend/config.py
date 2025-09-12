import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI/LLM Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///superannuation.db'
    
    # Redis Configuration (for caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'data/uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}
    
    # ML Model Configuration
    MODEL_PATH = 'models/'
    SCALER_PATH = 'models/scaler.joblib'
    MODEL_FILE = 'models/superannuation_model.joblib'
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
    
    # External API Keys
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    YAHOO_FINANCE_ENABLED = True
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    DATABASE_URL = 'sqlite:///test.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Production-specific settings
    SSL_REDIRECT = True
    
    # Enhanced security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }

# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

# Investment Types and Risk Profiles
INVESTMENT_TYPES = {
    'conservative': {
        'bonds': 0.7,
        'stocks': 0.2,
        'real_estate': 0.1,
        'expected_return': 0.045,
        'volatility': 0.08
    },
    'moderate': {
        'bonds': 0.4,
        'stocks': 0.5,
        'real_estate': 0.1,
        'expected_return': 0.065,
        'volatility': 0.12
    },
    'aggressive': {
        'bonds': 0.1,
        'stocks': 0.7,
        'real_estate': 0.2,
        'expected_return': 0.085,
        'volatility': 0.18
    }
}

# Risk Tolerance Mapping
RISK_TOLERANCE_MAPPING = {
    'Low': 'conservative',
    'Medium': 'moderate', 
    'High': 'aggressive'
}

# Educational Content Topics
EDUCATIONAL_TOPICS = [
    'superannuation_basics',
    'investment_types',
    'risk_management',
    'retirement_planning',
    'tax_benefits',
    'compound_interest',
    'portfolio_diversification',
    'market_volatility'
]

# Default Investment Options
DEFAULT_INVESTMENT_OPTIONS = [
    {
        'name': 'Conservative Growth',
        'type': 'Balanced',
        'risk_level': 'Low',
        'expected_return': 4.5,
        'fee': 0.75,
        'description': 'Lower risk option with steady growth potential'
    },
    {
        'name': 'Moderate Growth', 
        'type': 'Balanced',
        'risk_level': 'Medium',
        'expected_return': 6.5,
        'fee': 0.85,
        'description': 'Balanced approach with moderate risk and return'
    },
    {
        'name': 'High Growth',
        'type': 'Growth',
        'risk_level': 'High', 
        'expected_return': 8.5,
        'fee': 0.95,
        'description': 'Higher risk option targeting maximum growth'
    }
]