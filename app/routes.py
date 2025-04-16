from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from .auth import login_user, register_user, token_required
from .supabase_client import SupabaseManager
from .openai_client import OpenAIManager
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the landing page or redirect to home if already logged in"""
    if 'token' in session:
        return redirect(url_for('main.home'))
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests"""
    if request.method == 'POST':
        # Handle AJAX request
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            success, result = login_user(email, password)
            
            if success:
                session['token'] = result['token']
                session['user_id'] = result['user_id']
                return jsonify({'success': True, 'redirect': url_for('main.home')})
            else:
                return jsonify({'success': False, 'message': result}), 401
        
        # Handle form submission
        email = request.form.get('email')
        password = request.form.get('password')
        
        success, result = login_user(email, password)
        
        if success:
            session['token'] = result['token']
            session['user_id'] = result['user_id']
            return redirect(url_for('main.home'))
        else:
            flash(result)
            return redirect(url_for('main.login'))
    
    # GET request - render login page
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Handle registration requests"""
    if request.method == 'POST':
        # Handle AJAX request
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            nome = data.get('nome')
            telefone = data.get('telefone')
            instagram = data.get('instagram')
            
            success, result = register_user(email, password, nome, telefone, instagram)
            
            if success:
                # Check if there's a token (if not, email needs confirmation)
                if result.get('token'):
                    session['token'] = result['token']
                    session['user_id'] = result['user_id']
                    return jsonify({'success': True, 'redirect': url_for('main.home')})
                else:
                    # Respond with success, but indicating email confirmation is needed
                    return jsonify({
                        'success': True, 
                        'requireEmailConfirmation': True,
                        'message': result.get('message', 'Por favor, confirme seu email para continuar.'),
                        'redirect': url_for('main.register_success')
                    })
            else:
                return jsonify({'success': False, 'message': result}), 400
        
        # Handle form submission
        email = request.form.get('email')
        password = request.form.get('password')
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        instagram = request.form.get('instagram')
        
        success, result = register_user(email, password, nome, telefone, instagram)
        
        if success:
            # Check if there's a token (if not, email needs confirmation)
            if result.get('token'):
                session['token'] = result['token']
                session['user_id'] = result['user_id']
                return redirect(url_for('main.home'))
            else:
                # Redirect to registration success page instead of login
                return redirect(url_for('main.register_success'))
        else:
            flash(result)
            return redirect(url_for('main.register'))
    
    # GET request - render registration page
    return render_template('register.html')

@main.route('/home')
def home():
    """Render the home page (protected route)"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    return render_template('home.html', user=user_profile)

@main.route('/logout')
def logout():
    """Handle logout requests"""
    session.pop('token', None)
    session.pop('user_id', None)
    flash("You have been logged out")
    return redirect(url_for('main.index'))

@main.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    """API endpoint to get user profile"""
    return jsonify({
        'success': True,
        'user': current_user
    })

@main.route('/api/check-auth', methods=['GET'])
def check_auth():
    """API endpoint to check if user is authenticated"""
    if 'token' in session:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@main.route('/auth/confirm')
def confirm_email():
    """Handle email confirmation redirects from Supabase"""
    # Supabase passes parameters in the URL when redirecting after email confirmation
    token = request.args.get('token')
    type_param = request.args.get('type')
    
    if token and type_param == 'email_confirmation':
        try:
            # Verify the token with Supabase
            success, result = SupabaseManager.confirm_email(token)
            
            if success:
                flash("Email confirmado com sucesso! Agora você pode fazer login.", "success")
            else:
                flash(f"Erro ao confirmar email: {result}", "error")
        except Exception as e:
            flash(f"Erro ao confirmar email: {str(e)}", "error")
    else:
        flash("Link de confirmação inválido", "error")
    
    # Redirect to login page
    return redirect(url_for('main.login'))

@main.route('/register/success')
def register_success():
    """Show registration success page"""
    return render_template('register_success.html')

# Feature routes - placeholders for button functionality
@main.route('/capivara-editorial')
def capivara_editorial():
    """Render the Capivara Editorial feature page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    return render_template('features/capivara_editorial.html', user=user_profile)

@main.route('/skill-a')
def skill_a():
    """Render the Skill A (Instagram Analysis) feature page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page", "warning")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile", "danger")
        return redirect(url_for('main.login'))
    
    return render_template('features/skill_a.html', user=user_profile)

@main.route('/skill-a/analyze', methods=['POST'])
def analyze_instagram():
    """Handle Instagram analysis"""
    if 'token' not in session or 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Você precisa estar logado para usar esta funcionalidade'}), 401
    
    try:
        # Verificar se todos os arquivos foram enviados
        if 'bio_image' not in request.files or 'profile_image' not in request.files or 'feed_image' not in request.files:
            return jsonify({'success': False, 'error': 'Por favor, envie todas as três imagens requeridas'}), 400
        
        bio_image = request.files['bio_image']
        profile_image = request.files['profile_image']
        feed_image = request.files['feed_image']
        
        # Verificar se algum arquivo está vazio
        if bio_image.filename == '' or profile_image.filename == '' or feed_image.filename == '':
            return jsonify({'success': False, 'error': 'Por favor, selecione todas as três imagens requeridas'}), 400
        
        # Verificar extensões permitidas
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if not all(allowed_file(f.filename) for f in [bio_image, profile_image, feed_image]):
            return jsonify({'success': False, 'error': 'Apenas arquivos .png, .jpg e .jpeg são permitidos'}), 400
        
        # Verificar o tamanho dos arquivos
        max_file_size = 5 * 1024 * 1024  # 5MB por arquivo
        
        for img, img_name in [(bio_image, "Bio"), (profile_image, "Perfil"), (feed_image, "Feed")]:
            img.seek(0, 2)  # Move para o final do arquivo
            size = img.tell()  # Obtém a posição atual (tamanho)
            img.seek(0)  # Volta para o início
            
            if size > max_file_size:
                return jsonify({
                    'success': False, 
                    'error': f'A imagem {img_name} excede o limite de 5MB. Por favor, comprima a imagem ou selecione um arquivo menor.'
                }), 400
        
        # Chamar a API do OpenAI para análise
        success, result = OpenAIManager.analyze_instagram_images(bio_image, profile_image, feed_image)
        
        if success:
            # Retornar análise para o frontend
            return jsonify({
                'success': True,
                'analysis': result
            })
        else:
            return jsonify({'success': False, 'error': result}), 500
    
    except RequestEntityTooLarge:
        return jsonify({
            'success': False, 
            'error': 'O tamanho total das imagens excede o limite permitido (16MB). Por favor, comprima as imagens ou selecione arquivos menores.'
        }), 413
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Erro ao analisar Instagram: {error_details}")
        return jsonify({'success': False, 'error': f"Ocorreu um erro inesperado: {str(e)}"}), 500

@main.route('/skill-b')
def skill_b():
    """Render the Skill B feature page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    return render_template('features/skill_b.html', user=user_profile)

@main.route('/skill-c')
def skill_c():
    """Render the Skill C feature page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    return render_template('features/skill_c.html', user=user_profile)
