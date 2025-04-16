import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, session
from .supabase_client import SupabaseManager

def generate_token(user_id):
    """Generate a JWT token for the authenticated user"""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow(),
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            current_app.config.get('JWT_SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar token JWT: {str(e)}")
        return None

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token exists in session
        if 'token' in session:
            token = session['token']
        
        # Check if token is in request headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(
                token, 
                current_app.config.get('JWT_SECRET_KEY'),
                algorithms=['HS256']
            )
            
            # Get the user from the token
            current_user_id = data['sub']
            success, current_user = SupabaseManager.get_user_profile(current_user_id)
            
            if not success:
                return jsonify({'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token. Please log in again.'}), 401
        
        # Pass the current_user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

def login_user(email, password):
    """Login a user and generate token"""
    success, response = SupabaseManager.sign_in(email, password)
    
    if not success:
        return False, "Invalid credentials"
    
    # Get user data
    user = response.user
    user_id = user.id
    
    # Generate token
    token = generate_token(user_id)
    
    return True, {
        'token': token,
        'user_id': user_id
    }

def register_user(email, password, nome, telefone, instagram):
    """
    Register a new user with email confirmation
    
    Args:
        email (str): User's email
        password (str): User's password
        nome (str): User's name
        telefone (str): User's phone number
        instagram (str): User's Instagram handle
        
    Returns:
        tuple: (success, result)
    """
    try:
        # Tenta registrar o usuário no Supabase
        success, user_id, email_confirmed = SupabaseManager.sign_up(email, password, nome, telefone, instagram)
        
        if success:
            # Retorna uma mensagem especial indicando que o usuário precisa confirmar o email
            return True, {
                'user_id': user_id,
                'token': None,  # Sem token ainda, pois o email precisa ser confirmado
                'message': 'Um link de confirmação foi enviado para o seu email. Por favor, confirme seu email para continuar.'
            }
        else:
            return False, user_id  # Neste caso, user_id contém a mensagem de erro
    except Exception as e:
        return False, str(e)
