import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Supabase config
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # OpenAI API config
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit for file uploads

class ProductionConfig(Config):
    """Production configuration"""
    pass

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get current config
def get_config():
    """Returns the current configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env)
