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
    app.secret_key = app.config.get('SECRET_KEY') or 'chave-secreta-temporaria-para-desenvolvimento'
    
    # Depuração - imprima para verificar se a SECRET_KEY está definida
    print("SECRET_KEY está definida:", 'SECRET_KEY' in app.config)
    print("Valor da SECRET_KEY:", app.config.get('SECRET_KEY'))
    
    # Adicionar SECRET_KEY se não estiver na configuração
    if 'SECRET_KEY' not in app.config:
        app.config['SECRET_KEY'] = 'chave-secreta-temporaria-para-desenvolvimento'  # Em produção, use um valor aleatório forte
    
    # Garantir que MAX_CONTENT_LENGTH esteja configurado
    if 'MAX_CONTENT_LENGTH' not in app.config:
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Fallback para 16MB
    
    # Enable CORS with appropriate settings
    CORS(app, resources={r"/*": {"origins": "*"}})  # You can restrict origins as needed
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app