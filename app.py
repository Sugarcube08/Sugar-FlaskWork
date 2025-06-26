import flask
from route import web
from dotenv import load_dotenv
import os
import argparse
import subprocess
import platform
import base64
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from models import db
from flask_migrate import Migrate
from flask_wtf import CSRFProtect  # ✅ Added
from command.commands import (
                                run_setup,
                                generate_env,
                                create_controller,
                                create_model,
                                migrate_init, migrate_commit_and_apply,
                                create_html_template,
                                create_all,
                                create_component_template,
                                create_subtemplate,
                                create_admin
                            )

# === 🔒 Flask App Initialization ===
app = flask.Flask(__name__)
migrate = None
csrf = CSRFProtect()  # ✅ CSRFProtect instance

# Globals for crypto utilities
fernet = None
serializer = None

# === 🔐 Utility Functions ===
def encrypt_string(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt_string(token):
    return fernet.decrypt(token.encode()).decode()

def sign_token(data, salt="secure-token"):
    return serializer.dumps(data, salt=salt)

def verify_token(token, max_age=3600, salt="secure-token"):
    return serializer.loads(token, salt=salt, max_age=max_age)

# === ⚙️ Configuration Loader ===
def configure_app():
    global migrate, fernet, serializer

    load_dotenv()

    # Load and validate SECRET_KEY
    raw_key = os.getenv('SECRET_KEY')
    if not raw_key or not raw_key.startswith("base64:"):
        raise ValueError("❌ SECRET_KEY must be in base64 format (e.g., base64:YOUR_KEY)")

    try:
        decoded_key = base64.b64decode(raw_key.split("base64:")[1])
        if len(decoded_key) < 32:
            raise ValueError("SECRET_KEY must decode to at least 32 bytes.")
    except Exception as e:
        raise ValueError(f"❌ Invalid SECRET_KEY: {e}")

    # Build SQLAlchemy Database URI
    driver = os.getenv('DATABASE_DRIVER', 'sqlite')
    user = os.getenv('DATABASE_USER', '')
    password = os.getenv('DATABASE_PASSWORD', '')
    host = os.getenv('DATABASE_HOST', '')
    port = os.getenv('DATABASE_PORT', '')
    db_name = os.getenv('DATABASE_NAME', 'app_data')

    if driver == 'sqlite':
        instance_dir = os.path.abspath("instance")
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, f"{db_name}.db")
        print(f"🔍 Using SQLite DB path: {db_path}")
        database_uri = f"sqlite:///{db_path}"
    else:
        database_uri = f"{driver}://{user}:{password}@{host}:{port}/{db_name}"

    # App config
    app.config['SECRET_KEY'] = raw_key  # ✅ Keep it as a string for Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
    app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

    # Init DB and CSRF
    db.init_app(app)
    csrf.init_app(app)  # ✅ Initialize CSRF after config
    migrate = Migrate(app, db)

    # Init crypto utils
    fernet = Fernet(base64.urlsafe_b64encode(decoded_key[:32]))
    serializer = URLSafeTimedSerializer(decoded_key)

# === 🎨 Tailwind Watcher ===
def start_tailwind_watch():
    print("🎨 Starting Tailwind CSS in watch mode...")
    os_type = platform.system()
    try:
        if os_type == "Windows":
            env = os.environ.copy()
            node_path = os.path.expanduser('~/scoop/apps/nodejs/current')
            env['PATH'] = f"{node_path};{env['PATH']}"
            subprocess.Popen([
                "powershell", "-Command",
                "npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch"
            ], env=env)
        else:
            subprocess.Popen([
                "npx", "tailwindcss",
                "-i", "./static/src/input.css",
                "-o", "./static/css/output.css",
                "--watch"
            ])
    except Exception as e:
        print(f"⚠️ Tailwind watch failed to start: {e}")

# === 🧩 CLI Entry ===
def main():
    parser = argparse.ArgumentParser(
        description="🛠️ Flask Application Manager",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    subparsers.add_parser("setup", help="Install Python and Tailwind dependencies")

    parser_env = subparsers.add_parser("env:generate", help="Generate a secure .env file with SECRET_KEY")
    parser_env.add_argument('--force', action='store_true', help='Force overwrite existing .env file')

    parser_run = subparsers.add_parser("runserver", help="Start the Flask web server")
    parser_run.add_argument('--host', default='127.0.0.1', help='Set the host address (default: 127.0.0.1)')
    parser_run.add_argument('--port', type=int, default=5000, help='Set the port number (default: 5000)')

    parser_ctrl = subparsers.add_parser("create:controller", help="Generate a new controller")
    parser_ctrl.add_argument("name", help="Name of the controller")

    parser_template = subparsers.add_parser("create:template", help="Generate a new HTML template")
    parser_template.add_argument("name", help="Name of the template (without .html)")

    parser_model = subparsers.add_parser("create:model", help="Generate a new model")
    parser_model.add_argument("name", help="Name of the model")

    parser_all = subparsers.add_parser("create:all", help="Create controller, model, and template together")
    parser_all.add_argument("name", help="Name of the component to create")

    parser_component = subparsers.add_parser("create:component", help="Generate an HTML component in templates/components")
    parser_component.add_argument("name", help="Component name (without .html)")

    parser_subtemplate = subparsers.add_parser("create:subtemplate", help="Generate a subtemplate in templates/subtemplate")
    parser_subtemplate.add_argument("name", help="Subtemplate name (without .html)")
    
    parser_admin = subparsers.add_parser("create:admin", help="Create an admin user")
    parser_admin.add_argument("email", help="Admin email address")
    parser_admin.add_argument("password", help="Admin password")

    subparsers.add_parser("migrate:init", help="Initialize migration directory")
    subparsers.add_parser("migrate", help="Generate migration script and upgrade DB")


    args = parser.parse_args()

    if args.command == "setup":
        run_setup()

    elif args.command == "env:generate":
        generate_env(force=args.force)

    elif args.command == "runserver":
        configure_app()
        with app.app_context():
            db.create_all()
        web.setupRoute(app)
        start_tailwind_watch()
        print("🚀 Starting Flask server...")
        app.run(host=args.host, port=args.port)

    elif args.command == "create:controller":
        print(f"🧩 Creating controller: {args.name}")
        create_controller(args.name)

    elif args.command == "create:model":
        print(f"📦 Creating model: {args.name}")
        create_model(args.name)

    elif args.command == "migrate:init":
        configure_app()
        with app.app_context():
            migrate_init()

    elif args.command == "migrate":
        configure_app()
        with app.app_context():
            migrate_commit_and_apply()

    elif args.command == "create:template":
        print(f"🖼️ Creating template: {args.name}")
        create_html_template(args.name)

    elif args.command == "create:all":
        create_all(args.name)

    elif args.command == "create:component":
        print(f"🔧 Creating component: {args.name}")
        create_component_template(args.name)

    elif args.command == "create:subtemplate":
        print(f"🧩 Creating subtemplate: {args.name}")
        create_subtemplate(args.name)

    elif args.command == "create:admin":
        print("👤 Creating admin user...")
        configure_app()
        with app.app_context():
            create_admin(args.email, args.password)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
