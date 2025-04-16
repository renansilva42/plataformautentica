from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from .config import get_config
from .models.user import User

def create_app():
    """Create and configure the Flask application"""
    # Initialize app
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Set secret key for session management early
    app.secret_key = 'dev-secret-key'  # default before config load
    
    # Load config
    app.config.from_object(get_config())

    # Override secret key from config if available
    if app.config.get('SECRET_KEY'):
        app.secret_key = app.config['SECRET_KEY']


    # Garantir que MAX_CONTENT_LENGTH esteja configurado
    if 'MAX_CONTENT_LENGTH' not in app.config:
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Fallback para 16MB
    
    # Enable CORS with appropriate settings
    CORS(app, resources={r"/*": {"origins": "*"}})  # You can restrict origins as needed
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
