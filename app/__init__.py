from flask import Flask
from flask_cors import CORS
from .config import get_config

def create_app():
    """Create and configure the Flask application"""
    # Initialize app
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Load config
    app.config.from_object(get_config())
    
    # Enable CORS with appropriate settings
    CORS(app, resources={r"/*": {"origins": "*"}})  # You can restrict origins as needed
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
