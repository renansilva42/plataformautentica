from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from .auth import login_user, register_user, token_required
from .supabase_client import SupabaseManager

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
    """Render the Skill A feature page"""
    if 'token' not in session or 'user_id' not in session:
        flash("Please log in to access this page")
        return redirect(url_for('main.login'))
    
    # Get user profile
    user_id = session['user_id']
    success, user_profile = SupabaseManager.get_user_profile(user_id)
    
    if not success:
        flash("Error loading user profile")
        return redirect(url_for('main.login'))
    
    return render_template('features/skill_a.html', user=user_profile)

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
