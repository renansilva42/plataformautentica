from flask_login import UserMixin
from datetime import datetime

# If you're using SQLAlchemy, uncomment this:
# from .. import db

# This is a placeholder User model. You'll need to adapt it to your database setup.
# If you're using SQLAlchemy, replace this with a proper db.Model class
class User(UserMixin):
    """User model for authentication and authorization"""
    
    # If using SQLAlchemy:
    # __tablename__ = 'users'
    # id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    # name = db.Column(db.String(80), nullable=False)
    # password = db.Column(db.String(120), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # is_active = db.Column(db.Boolean, default=True)
    
    # Simple implementation for development purposes
    # Replace this with your database integration
    _users = {}  # In-memory storage for demo purposes
    
    def __init__(self, id=None, email=None, name=None, password=None):
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.is_active = True
        self.created_at = datetime.utcnow()
        
        if id is not None:
            User._users[id] = self
    
    @classmethod
    def query(cls):
        class QueryHelper:
            @staticmethod
            def get(id):
                return User._users.get(id)
                
            @staticmethod
            def filter_by(**kwargs):
                class FilterHelper:
                    @staticmethod
                    def first():
                        for user in User._users.values():
                            match = True
                            for key, value in kwargs.items():
                                if getattr(user, key) != value:
                                    match = False
                                    break
                            if match:
                                return user
                        return None
                return FilterHelper()
        
        return QueryHelper()
    
    def __repr__(self):
        return f'<User {self.email}>'