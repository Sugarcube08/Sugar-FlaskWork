from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

__all__ = []
from .admin import Admin
__all__.append('Admin')
