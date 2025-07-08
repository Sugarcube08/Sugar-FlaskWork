from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

__all__ = []
from .user import User
__all__.append('User')
from .admin import Admin
__all__.append('Admin')
from .userprofile import UserProfile
__all__.append('Userprofile')
from .attendancetoken import Attendancetoken
__all__.append('Attendancetoken')
from .attendancerecord import Attendancerecord
__all__.append('Attendancerecord')
