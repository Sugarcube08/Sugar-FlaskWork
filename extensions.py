from flask_migrate import Migrate
from flask_wtf import CSRFProtect

migrate = Migrate()
csrf = CSRFProtect()
