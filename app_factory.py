# app_factory.py
import os
import base64
from dotenv import load_dotenv
from flask import Flask
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from extensions import migrate, csrf
from models import db
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

fernet = None
serializer = None

def create_app():
    global fernet, serializer

    load_dotenv()

    # Validate and load SECRET_KEY
    raw_key = os.getenv("SECRET_KEY")
    if not raw_key or not raw_key.startswith("base64:"):
        raise ValueError("SECRET_KEY must be in base64 format")

    decoded_key = base64.b64decode(raw_key.split("base64:")[1])
    if len(decoded_key) < 32:
        raise ValueError("SECRET_KEY must decode to at least 32 bytes")

    # Configure database URI
    database_uri = _build_database_uri()

    # Create Flask app and config
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=raw_key,
        HOST=os.getenv("HOST"),
        PORT=int(os.getenv("PORT", 5000)),
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True",
        FLASK_ENV=os.getenv("FLASK_ENV", "development"),
        FLASK_DEBUG=os.getenv("FLASK_DEBUG", "True") == "True",
        UPLOAD_FOLDER=os.path.join(app.root_path, os.getenv("UPLOAD_FOLDER", "static/uploads")),
        ALLOWED_EXTENSIONS=set(os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif").split(",")),
    )

    # Create DB if needed (except SQLite)
    if not database_uri.startswith("sqlite"):
        engine = create_engine(database_uri)
        if not database_exists(engine.url):
            create_database(engine.url)

    # Ensure the base upload folder exists at app startup
    # This will create E:\CODE\sugarcodez-web\static\uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print(f"DEBUG (app_factory): Base UPLOAD_FOLDER ensured: {app.config['UPLOAD_FOLDER']}")


    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Initialize crypto utilities
    fernet = Fernet(base64.urlsafe_b64encode(decoded_key[:32]))
    serializer = URLSafeTimedSerializer(decoded_key)

    return app

def _build_database_uri():
    driver = os.getenv("DATABASE_DRIVER", "sqlite").lower()
    user = os.getenv("DATABASE_USER", "")
    password = os.getenv("DATABASE_PASSWORD", "")
    host = os.getenv("DATABASE_HOST", "")
    port = os.getenv("DATABASE_PORT", "")
    db_name = os.getenv("DATABASE_NAME", "app_data")

    if driver == "sqlite":
        instance_dir = os.path.abspath("instance")
        os.makedirs(instance_dir, exist_ok=True)
        return f"sqlite:///{os.path.join(instance_dir, f'{db_name}.db')}"

    elif driver in ["mysql", "mariadb"]:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

    elif driver in ["postgres", "postgresql"]:
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

    else:
        raise ValueError(f"Unsupported DATABASE_DRIVER: {driver}")