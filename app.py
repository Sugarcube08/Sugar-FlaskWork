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
from command.commands import run_setup, generate_env, create_controller

# === 🔒 Flask Config ===
app = flask.Flask(__name__)

# Crypto utilities (will be initialized later)
fernet = None
serializer = None

def encrypt_string(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt_string(token):
    return fernet.decrypt(token.encode()).decode()

def sign_token(data, salt="secure-token"):
    return serializer.dumps(data, salt=salt)

def verify_token(token, max_age=3600, salt="secure-token"):
    return serializer.loads(token, salt=salt, max_age=max_age)



# === 🧠 CLI Interface ===
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="🛠️ Flask Application Manager\n\n"
                    "Use this tool to either run the web server or perform project setup.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # runserver
    parser_run = subparsers.add_parser("runserver", help="Start the Flask web server")
    parser_run.add_argument('--host', default='127.0.0.1', help='Set the host address (default: 127.0.0.1)')
    parser_run.add_argument('--port', type=int, default=5000, help='Set the port number (default: 5000)')
    
    # setup
    parser_setup = subparsers.add_parser("setup", help="Install Python and Tailwind dependencies")

    # env:generate
    parser_env = subparsers.add_parser("env:generate", help="Generate a secure .env file with SECRET_KEY")
    parser_env.add_argument('--force', action='store_true', help='Force overwrite existing .env file')
    
    # create:controller
    parser_ctrl = subparsers.add_parser("create:controller", help="Generate controller/model/templates")
    parser_ctrl.add_argument("name", help="Name of the component")
    parser_ctrl.add_argument("-x", "--extras", help="Component flags: c=controller, m=model, t=template, a=all", default="c")

    args = parser.parse_args()

    if args.command == "setup":
        run_setup()

    elif args.command == "env:generate":
        generate_env(force=args.force)

    elif args.command == "runserver":
        load_dotenv()

        raw_key = os.getenv('SECRET_KEY')
        if not raw_key or not raw_key.startswith("base64:"):
            raise ValueError("❌ ERROR: SECRET_KEY must be in base64 format (e.g., base64:YOUR_KEY) in .env")

        try:
            decoded_key = base64.b64decode(raw_key.split("base64:")[1])
            if len(decoded_key) < 32:
                raise ValueError("SECRET_KEY must decode to at least 32 bytes.")
        except Exception as e:
            raise ValueError(f"❌ Invalid SECRET_KEY: {e}")

        # Configure Flask
        app.config['SECRET_KEY'] = decoded_key
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
        app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
        app.config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

        # Init Crypto
        fernet = Fernet(base64.urlsafe_b64encode(decoded_key[:32]))
        serializer = URLSafeTimedSerializer(decoded_key)

        # Setup routes
        web.setupRoute(app)
        print("🎨 Starting Tailwind CSS in watch mode...")
        os_type = platform.system()
        if os_type == "Windows":
            env = os.environ.copy()
            node_path = os.path.expanduser('~/scoop/apps/nodejs/current')
            env['PATH'] = f"{node_path};{env['PATH']}"
            subprocess.Popen([    
            "powershell", "-Command",
            "npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css"
            ], env=env)
        elif os_type == "Linux":
            print("🎨 Starting Tailwind CSS in watch mode...")
            subprocess.Popen([
                "npx", "tailwindcss",
                "-i", "./static/src/input.css",
                "-o", "./static/css/output.css",
                "--watch"
            ])

        # 🚀 Start Flask server
        print("🚀 Starting Flask server...")
        # Run
        app.run(host=args.host, port=args.port)
    
    elif args.command == "create:controller":
        name = args.name
        flags = args.extras.lower()

        if 'a' in flags:
            print("🧱 Generating full MVC stack (model, controller, template)...")
            # generate_model(name)
            create_controller(name)
            # generate_templates(name)

        else:
            if 'm' in flags:
                print("📦 Generating model...")
                # generate_model(name)

            if 'c' in flags:
                print("🧩 Generating controller...")
                create_controller(name)

            if 't' in flags:
                print("🎨 Generating templates...")
                # generate_templates(name)

            if not any(c in flags for c in 'mct'):
                print("⚠️  No valid components found in flags. Use combinations of: c, m, t, a.")


    else:
        parser.print_help()