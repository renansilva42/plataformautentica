from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

# Create a Blueprint named 'main'
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Route for the home page"""
    return render_template('index.html')

@main.route('/about')
def about():
    """Route for the about page"""
    return render_template('about.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Route for user login"""
    from flask_login import login_user as flask_login_user
    from app.auth import login_user as auth_login_user
    from app.models.user import User

    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        success, result = auth_login_user(email, password)
        if success:
            user_id = result.get('user_id')
            user = User.query.get(user_id)
            if user:
                flask_login_user(user, remember=remember)
                return redirect(url_for('main.index'))
        
        flash('Erro ao fazer login. Tente novamente.', 'danger')
        return redirect(url_for('main.login'))
    
    # Handle GET request (show login page)
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Route for user registration"""
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        # Here you would typically create a new user
        # For example:
        # name = request.form.get('name')
        # email = request.form.get('email')
        # password = request.form.get('password')
        # 
        # new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        # db.session.add(new_user)
        # db.session.commit()
        
        flash('Registro realizado com sucesso!', 'success')
        return redirect(url_for('main.login'))
    
    # Handle GET request (show registration page)
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    """Route for user logout"""
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/debug-secret-key')
def debug_secret_key():
    from flask import current_app
    return f"Secret Key: {current_app.secret_key}"

# Add more routes as needed
