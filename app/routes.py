from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, session, current_app, request, send_from_directory
from .auth import login_user, register_user, token_required
from .supabase_client import SupabaseManager
from .openai_client import OpenAIManager
import os
import base64
import uuid
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

    # Pass access_expiration to template
    access_expiration = user_profile.get('access_expiration')

    return render_template('home.html', user=user_profile, access_expiration=access_expiration)

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

from datetime import datetime
from zoneinfo import ZoneInfo

@main.route('/capivara-analista')
def capivara_analista():
    """Render the Capivara Analista chat page"""
    from flask import current_app
    import logging
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    access_expiration_str = user_profile.get('access_expiration')
    current_app.logger.debug(f"Access expiration string: {access_expiration_str}")
    if access_expiration_str:
        try:
            access_expiration = datetime.fromisoformat(access_expiration_str)
            # Make access_expiration timezone-aware in America/Belem timezone if naive
            if access_expiration.tzinfo is None:
                access_expiration = access_expiration.replace(tzinfo=ZoneInfo("America/Belem"))
            now = datetime.now(ZoneInfo("America/Belem"))
            current_app.logger.debug(f"Current time: {now}, Access expiration: {access_expiration}")
            if now > access_expiration:
                current_app.logger.info("Access expired, redirecting to home")
                flash("Seu acesso expirou. Redirecionando para a página inicial.")
                return redirect(url_for('main.home'))
        except Exception as e:
            current_app.logger.error(f"Error parsing access_expiration: {e}")
            # If parsing fails, allow access (or optionally block)
            pass
    
    return render_template('features/capivara_analista.html', user=user_profile)

@main.route('/capivara-analista/chat', methods=['POST'])
def capivara_analista_chat():
    """Handle chat messages for Capivara Analista"""
    if 'token' not in session or 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    if not success:
        return jsonify({'success': False, 'error': 'User profile not found'}), 404

    # Check if the request is JSON with base64 image data
    if request.is_json:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        message = data['message']
        message_type = data.get('type', 'text')  # 'text' or 'image' or 'image_base64'
        thread_id = data.get('thread_id')
        if not thread_id:
            import uuid
            thread_id = str(uuid.uuid4())

        # If image type and message is base64 data URI, extract base64 string and send as 'image_file'
        if message_type == 'image' and isinstance(message, str) and message.startswith('data:image/'):
            # Extract base64 data
            header, encoded = message.split(',', 1)
            file_ext = header.split('/')[1].split(';')[0]  # e.g. jpeg, png
            if file_ext not in ['jpeg', 'jpg', 'png']:
                return jsonify({'success': False, 'error': 'Unsupported image format'}), 400

            # Validate base64
            try:
                base64.b64decode(encoded)
            except Exception:
                return jsonify({'success': False, 'error': 'Invalid base64 image data'}), 400

            # Send base64 string directly to OpenAIManager with message_type 'image_file'
            message = encoded
            message_type = 'image_file'

        elif message_type == 'image':
            # If image type but not base64 data URI, reject
            return jsonify({'success': False, 'error': 'Invalid image data. Expected base64 data URI.'}), 400

    # Fallback: multipart/form-data image upload (deprecated, optional)
    elif request.content_type.startswith('multipart/form-data'):
        # Expecting an image file in 'image' field
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        image_file = request.files['image']

        # Validate file extension
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

        if not allowed_file(image_file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only png, jpg, jpeg allowed.'}), 400

        # Read image bytes and encode as base64 data URI
        img_bytes = image_file.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        message = img_base64
        message_type = 'image_file'

    else:
        return jsonify({'success': False, 'error': 'Unsupported content type'}), 400

    # Save user message to DB
    save_success, save_result = SupabaseManager.insert_message(user_id, thread_id, 'user', message)
    if not save_success:
        current_app.logger.error(f"Failed to save user message: {save_result}")

    # Call OpenAIManager method to get assistant response
    from .openai_client import OpenAIManager
    try:
        response = OpenAIManager.capivara_analista_chat(message, message_type, user_profile)

        # Save AI response to DB
        save_success, save_result = SupabaseManager.insert_message(user_id, thread_id, 'ai', response)
        if not save_success:
            current_app.logger.error(f"Failed to save AI response: {save_result}")

        return jsonify({'success': True, 'response': response, 'thread_id': thread_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    return send_from_directory(upload_folder, filename)

@main.route('/capivara-conteudo')
def capivara_conteudo():
    """Render the Capivara do Conteúdo chat page"""
    from flask import current_app
    import logging
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    access_expiration_str = user_profile.get('access_expiration')
    current_app.logger.debug(f"Access expiration string: {access_expiration_str}")
    if access_expiration_str:
        try:
            access_expiration = datetime.fromisoformat(access_expiration_str)
            now = datetime.now(ZoneInfo("America/Belem"))
            # Make access_expiration timezone-aware in America/Belem timezone if naive
            if access_expiration.tzinfo is None:
                access_expiration = access_expiration.replace(tzinfo=ZoneInfo("America/Belem"))
            current_app.logger.debug(f"Current time: {now}, Access expiration: {access_expiration}")
            if now > access_expiration:
                current_app.logger.info("Access expired, redirecting to home")
                flash("Seu acesso expirou. Redirecionando para a página inicial.")
                return redirect(url_for('main.home'))
        except Exception as e:
            current_app.logger.error(f"Error parsing access_expiration: {e}")
            # If parsing fails, allow access (or optionally block)
            pass
    
    return render_template('features/capivara_conteudo.html', user=user_profile)

@main.route('/capivara-conteudo/chat', methods=['POST'])
def capivara_conteudo_chat():
    """Handle chat messages for Capivara do Conteúdo"""
    if 'token' not in session or 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    if not success:
        return jsonify({'success': False, 'error': 'User profile not found'}), 404

    if not request.is_json:
        return jsonify({'success': False, 'error': 'Invalid request format'}), 400

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'No message provided'}), 400

    message = data['message']
    message_type = data.get('type', 'text')  # Only 'text' expected, no images
    thread_id = data.get('thread_id')
    if not thread_id:
        import uuid
        thread_id = str(uuid.uuid4())

    # Save user message to DB
    save_success, save_result = SupabaseManager.insert_message(user_id, thread_id, 'user', message)
    if not save_success:
        current_app.logger.error(f"Failed to save user message: {save_result}")

    from .openai_client import OpenAIManager
    try:
        response = OpenAIManager.capivara_conteudo_chat(message, message_type, user_profile)

        # Save AI response to DB
        save_success, save_result = SupabaseManager.insert_message(user_id, thread_id, 'ai', response)
        if not save_success:
            current_app.logger.error(f"Failed to save AI response: {save_result}")

        return jsonify({'success': True, 'response': response, 'thread_id': thread_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/profile', methods=['GET'])
def profile():
    """Render the user profile page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access your profile")
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)

    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))

    return render_template('features/profile.html', user=user_profile)

@main.route('/profile/upload-photo', methods=['POST'])
def upload_profile_photo():
    """Handle profile photo upload"""
    if 'token' not in session or 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No photo file provided'}), 400

    photo = request.files['photo']

    # Validate file extension
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    if not allowed_file(photo.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Only png, jpg, jpeg allowed.'}), 400

    # Secure the filename
    filename = secure_filename(photo.filename)
    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/img/profile_photos')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Delete old profile photo file if exists
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    old_photo_url = None
    is_first_upload = True
    if success:
        old_photo_url = user_profile.get('profile_photo_url')
        if old_photo_url:
            is_first_upload = False
            # Extract filename from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(old_photo_url)
            old_filename = os.path.basename(parsed_url.path)
            old_file_path = os.path.join(upload_folder, old_filename)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    current_app.logger.info(f"Deleted old profile photo: {old_file_path}")
                except Exception as e:
                    current_app.logger.error(f"Error deleting old profile photo: {e}")

    file_path = os.path.join(upload_folder, unique_filename)
    photo.save(file_path)

    # Update user profile photo URL in Supabase
    photo_url = url_for('static', filename=f'img/profile_photos/{unique_filename}')

    success, result = SupabaseManager.update_user_profile(user_id, {'profile_photo_url': photo_url})

    if not success:
        current_app.logger.error(f"Failed to update profile photo: {result}")
        return jsonify({'success': False, 'error': f'Failed to update profile photo: {result}'}), 500

    return jsonify({
        'success': True,
        'photo_url': photo_url,
        'is_first_upload': is_first_upload,
        'old_photo_url': old_photo_url
    })
