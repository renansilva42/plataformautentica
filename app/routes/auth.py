@auth_bp.route('/logout')
def logout():
    logger.debug(f"Logging out user: {session.get('email', 'Unknown')}")
    
    # Clear the session
    session.clear()
    
    logger.debug(f"Session after logout: {session}")
    
    # Redirect to login page
    return redirect(url_for('auth.login'))