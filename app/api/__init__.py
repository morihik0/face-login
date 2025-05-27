"""
API package for Face Login system.
This module defines the API blueprints for the application.
"""
from flask import Blueprint

# Create blueprints
users_bp = Blueprint('users', __name__)
recognition_bp = Blueprint('recognition', __name__)
auth_bp = Blueprint('auth', __name__)
public_bp = Blueprint('public', __name__)

# Import routes to register them with the blueprints
from app.api import users_routes, recognition_routes, auth_routes, public_routes