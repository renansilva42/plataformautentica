import logging
from functools import wraps
from flask import session, redirect, url_for, request, g

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log the current session state
        logger.debug(f"Current session: {session}")
        logger.debug(f"Is authenticated: {session.get('authenticated', False)}")
        
        if not session.get('authenticated', False):
            logger.warning(f"Unauthenticated access attempt to {request.path}")
            # Store the original requested URL to redirect after login
            return redirect(url_for('auth.login', next=request.url))
        
        # User is authenticated, store in g for easy access in routes
        g.user_id = session.get('user_id')
        g.email = session.get('email')
        
        logger.debug(f"Authenticated access to {request.path} by user {g.email}")
        return f(*args, **kwargs)
    
    return decorated_function