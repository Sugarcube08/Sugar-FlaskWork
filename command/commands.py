import os
import subprocess
import platform
import sys
import base64
import shutil
import time
from flask_migrate import init, stamp
from flask_migrate import migrate 
from flask_migrate import upgrade 
from flask import current_app
from models import Admin, db

# === 🛠️ Setup Command ===
def run(cmd, shell=True, env=None):
    """Execute a shell command safely with logging."""
    print(f"→ {cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(e)
        sys.exit(1)

def load_dependencies(yaml_path="./dependencies.yml"):
    """Load dependencies from YAML file."""
    if not os.path.exists(yaml_path):
        print(f"❌ Missing dependency file: {yaml_path}")
        sys.exit(1)
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)

def install_python(python_deps):
    """Install Python dependencies from requirements.txt."""
    print("🐍 Installing Python dependencies...")
    if "requirements" in python_deps and os.path.exists(python_deps["requirements"]):
        run(f"{sys.executable} -m pip install -r {python_deps['requirements']}")
    else:
        print("⚠ No Python requirements found.")

def install_system(system_deps):
    """Install system-level dependencies dynamically."""
    os_type = platform.system().lower()
    print(f"🧩 Detected OS: {os_type}")

    for name, cmd_map in system_deps.items():
        cmd = cmd_map.get(os_type) or cmd_map.get("all")
        if not cmd:
            continue

        # Skip if already installed
        if shutil.which(name):
            print(f"✔ {name} already installed.")
            continue

        print(f"🔧 Installing {name}...")
        run(cmd)

def run_build_steps(build_steps):
    """Run post-install build commands (like Tailwind build)."""
    os_type = platform.system().lower()
    for name, cmd_map in build_steps.items():
        cmd = cmd_map.get(os_type) or cmd_map.get("all")
        if not cmd:
            continue
        print(f"🏗️ Building {name} assets...")
        run(cmd)

def run_setup():
    deps = load_dependencies()
    env = os.environ.copy()

    # --- Python dependencies ---
    if "python" in deps:
        install_python(deps["python"])

    # --- System dependencies ---
    if "system" in deps:
        install_system(deps["system"])

    # --- Tailwind initialization ---
    if not os.path.exists("./static/src/input.css"):
        os.makedirs("./static/src", exist_ok=True)
        with open("./static/src/input.css", "w") as f:
            f.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")

    # --- Build steps ---
    if "build" in deps:
        run_build_steps(deps["build"])

    print("✅ Sugar-Flaskwork setup completed successfully!")
# === 📄 .env Generator Command ===
def generate_env(force=False):
    example_path = '.env.example'
    target_path = '.env'

    if not os.path.exists(target_path) or force:
        if os.path.exists(example_path):
            print("📄 Creating .env from .env.example...")
            with open(example_path, 'r') as src, open(target_path, 'w') as dest:
                dest.write(src.read())
        else:
            print("⚠️ .env.example not found. Cannot proceed.")
            return
    else:
        print("✅ .env already exists. Updating SECRET_KEY only...")

    # Generate new key
    new_key = base64.b64encode(os.urandom(32)).decode()
    full_key = f"SECRET_KEY=base64:{new_key}"

    # Replace or append SECRET_KEY
    with open(target_path, 'r') as file:
        lines = file.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith("SECRET_KEY="):
            lines[i] = full_key + "\n"
            updated = True
            break

    if not updated:
        lines.append("\n" + full_key + "\n")

    with open(target_path, 'w') as file:
        file.writelines(lines)

    print(f"🔐 SECRET_KEY generated and written to .env ✅")
    print(f"🔑 Preview: base64:{new_key[:6]}...{new_key[-6:]}")


def create_controller(name):
    if '/' in name or '\\' in name:
        path = name.replace('/','.').replace('\\', '.')
        name = path.split('.')[-1]  # Get the last part as the controller name
        # 💡 Format controller name properly
        class_name = name.capitalize() + "Controller"
        file_stem = path.lower() + "Controller"
        file_name = f"{file_stem.replace('.','/')}.py"
    else:
        # 💡 Format controller name properly
        class_name = name.capitalize() + "Controller"
        file_stem = name.lower() + "Controller"
        file_name = f"{file_stem}.py"

    # 🛣️ Paths
    base_dir = os.path.dirname(os.path.dirname(__file__))  # go up to project root
    controller_dir = os.path.join(base_dir, 'controller')
    template_path = os.path.join(base_dir, 'command', 'template', 'Controller.txt')
    output_path = os.path.join(controller_dir, file_name)
    init_path = os.path.join(controller_dir, '__init__.py')

    # ✅ Ensure controller folder exists
    os.makedirs(controller_dir, exist_ok=True)

    # 📖 Read template
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"❌ Template not found at: {template_path}")

    with open(template_path, 'r') as f:
        template = f.read()

    # 📝 Replace placeholders
    content = template.replace('{className}', class_name).replace('{name}', name)

    # 💾 Write to new controller file
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Created: controller/{file_name}")

    # 🔁 Auto-register in __init__.py
    import_line = f"from .{file_stem} import {class_name}"
    append_line = f"__all__.append('{class_name}')"

    # 📄 Read or create __init__.py
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("__all__ = []\n")

    with open(init_path, 'r') as f:
        init_content = f.read()

    if import_line not in init_content:
        with open(init_path, 'a') as f:
            if not init_content.endswith('\n'):
                f.write('\n')
            f.write(f"{import_line}\n{append_line}\n")
        print(f"🔗 Registered {class_name} in controller/__init__.py")
    else:
        print(f"ℹ️ {class_name} already registered in controller/__init__.py")

def create_model(name):
    if '/' in name or '\\' in name:
        path = name.replace('/', '.').replace('\\', '.')
        name = path.split('.')[-1]
        class_name = name.capitalize()
        file_stem = path.lower()
        file_name = f"{file_stem.replace('.', '/')}.py"
    else:
        class_name = name.capitalize()
        file_stem = name.lower()
        file_name = f"{file_stem}.py"

    base_dir = os.path.dirname(os.path.dirname(__file__))
    model_dir = os.path.join(base_dir, 'models')
    template_path = os.path.join(base_dir, 'command', 'template', 'Model.txt')
    output_path = os.path.join(model_dir, file_name)
    init_path = os.path.join(model_dir, '__init__.py')

    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"❌ Template not found at: {template_path}")

    with open(template_path, 'r') as f:
        template = f.read()

    content = template.replace('{className}', class_name).replace('{name}', name.lower())

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Created: models/{file_name}")

    import_line = f"from .{file_stem} import {class_name}"
    append_line = f"__all__.append('{class_name}')"

    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("from flask_sqlalchemy import SQLAlchemy\ndb = SQLAlchemy()\n__all__ = []\n")

    with open(init_path, 'r') as f:
        init_content = f.read()

    if import_line not in init_content:
        with open(init_path, 'a') as f:
            if not init_content.endswith('\n'):
                f.write('\n')
            f.write(f"{import_line}\n{append_line}\n")
        print(f"🔗 Registered {class_name} in models/__init__.py")
    else:
        print(f"ℹ️ {class_name} already registered in models/__init__.py")

def migrate_init():
    migrations_path = os.path.join(current_app.root_path, 'migrations')
    if os.path.exists(migrations_path):
        print("ℹ️ Migrations directory already exists.")
    else:
        print("📁 Initializing migrations directory...")
        init()
        print("✅ Migration directory initialized.")


def migrate_commit_and_apply(message):
    print("🔍 Attempting to upgrade database to latest version...")
    try:
        upgrade()
        print("✅ Database is now up to date with existing migrations.")
    except Exception as e:
        print(f"⚠️ Failed to upgrade DB: {e}")
        if "Can't locate revision identified by" in str(e):
            print("📌 The database revision is out of sync with your local migration files.")
            choice = input("Do you want to stamp DB to the current head and continue? (yes/no): ").strip().lower()
            if choice == "yes":
                try:
                    stamp(revision="head")
                    print("✅ Database stamped to head. Attempting upgrade again.")
                    upgrade() # Try upgrading again after stamping
                    print("✅ Database successfully upgraded after stamping.")
                except Exception as e_after_stamp:
                    print(f"❌ Failed to upgrade after stamping: {e_after_stamp}. Aborting.")
                    return
            else:
                print("❌ Migration aborted due to revision mismatch.")
                return
        elif "table already exists" in str(e).lower(): # Specific handling for your error
            print("🚫 Error: A table already exists that a migration is trying to create.")
            print("This often means a migration was run partially or the DB schema is out of sync.")
            print("Consider manually reviewing your DB or resetting development databases.")
            return
        else:
            print("❌ Unexpected error during upgrade. Aborting.")
            return

    # Only proceed to autogenerate if upgrade was successful or handled
    print("\n📝 Checking for schema changes and generating new migration script...")
    commit_msg = message if message and message != "Default migration message" else None
    try:
        # Autogenerate will only create a script if there are actual model changes
        migrate(message=commit_msg or "Auto migration")
        print("✅ New migration script generated if schema changes were detected.")
        print("Remember to review the generated script and run 'upgrade' to apply it.")
    except Exception as e:
        print(f"❌ Failed to generate migration script: {e}")
    
def create_html_template(name):
    if not name.isidentifier():
        print("❌ Invalid template name. Use letters, numbers, and underscores only.")
        return

    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Paths
    template_txt_path = os.path.join(base_dir, 'command', 'template', 'Template.txt')
    templates_dir = os.path.join(base_dir, 'templates')
    output_file_path = os.path.join(templates_dir, f'{name}.html')

    # Ensure template.txt exists
    if not os.path.exists(template_txt_path):
        print(f"❌ Template base file not found at: {template_txt_path}")
        return

    os.makedirs(templates_dir, exist_ok=True)

    # Don't overwrite if already exists
    if os.path.exists(output_file_path):
        print(f"⚠️ Template '{name}.html' already exists at: {output_file_path}")
        return

    # Load and render
    with open(template_txt_path, 'r') as f:
        template_content = f.read()

    rendered_content = template_content.replace('{name}', name)

    # Write new HTML file
    with open(output_file_path, 'w') as f:
        f.write(rendered_content)

    print(f"✅ Template '{name}.html' created at: {output_file_path}")

def create_all(name):
    print(f"\n🔧 Creating full component set for: {name}")
    
    try:
        create_controller(name)
        create_model(name)
        create_html_template(name)
        print(f"\n✅ All components for '{name}' created successfully!")
    except Exception as e:
        print(f"❌ Failed to create all components: {e}")

def create_component_template(name):
    if not name.isidentifier():
        print("❌ Invalid component name. Use only letters, numbers, and underscores.")
        return

    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_txt_path = os.path.join(base_dir, 'command', 'template', 'Component.txt')
    components_dir = os.path.join(base_dir, 'templates', 'components')
    output_path = os.path.join(components_dir, f"{name}.html")

    if not os.path.exists(template_txt_path):
        print(f"❌ Component.txt not found at: {template_txt_path}")
        return

    os.makedirs(components_dir, exist_ok=True)

    if os.path.exists(output_path):
        print(f"⚠️ Component '{name}.html' already exists.")
        return

    with open(template_txt_path, 'r') as f:
        content = f.read().replace("{name}", name)

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Component created: templates/components/{name}.html")


def create_subtemplate(name):
    if not name.isidentifier():
        print("❌ Invalid subtemplate name. Use only letters, numbers, and underscores.")
        return

    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_txt_path = os.path.join(base_dir, 'command', 'template', 'subTemplate.txt')
    subtemplate_dir = os.path.join(base_dir, 'templates', 'subtemplate')
    output_path = os.path.join(subtemplate_dir, f"{name}.html")

    if not os.path.exists(template_txt_path):
        print(f"❌ subTemplate.txt not found at: {template_txt_path}")
        return

    os.makedirs(subtemplate_dir, exist_ok=True)

    if os.path.exists(output_path):
        print(f"⚠️ Subtemplate '{name}.html' already exists.")
        return

    with open(template_txt_path, 'r') as f:
        content = f.read().replace("{name}", name)

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Subtemplate created: templates/subtemplate/{name}.html")

def create_admin(email, password, post="Core Member"):
    if not email or not password:
        print("❌ Email and password are required to create an admin.")
        return

    try:
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            print(f"⚠️ Admin with email '{email}' already exists.")
            return

        # Create new admin
        new_admin = Admin(email=email, post=post)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ Admin created successfully: {email}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create admin: {e}")
        
def drop_all_tables(app):
    migrations_path = os.path.join(current_app.root_path, 'migrations')
    with app.app_context():
        confirm = input("⚠️ This will DROP the entire DATABASE! Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            print("❌ Drop aborted.")
            return

        engine = db.get_engine()
        db_name = engine.url.database
        db_driver = engine.url.drivername

        # Close the current session and dispose the engine
        db.session.close()
        engine.dispose()

        print(f"🧨 Dropping database '{db_name}'...")
        if os.path.exists(migrations_path):
            print("📁 Deleting migrations directory...")
            shutil.rmtree(migrations_path)

        try:
            if db_driver == 'sqlite':
                # For SQLite, delete the database file
                if os.path.exists(db_name):
                    os.remove(db_name)
                    print(f"✅ Database '{db_name}' dropped successfully.")
                else:
                    print(f"⚠️ Database file '{db_name}' does not exist.")
            else:
                # For other databases, use SQL commands
                from sqlalchemy import create_engine
                neutral_url = engine.url.set(database=None)
                neutral_engine = create_engine(neutral_url)

                with neutral_engine.connect() as conn:
                    conn.execution_options(isolation_level="AUTOCOMMIT")
                    conn.exec_driver_sql(f"DROP DATABASE IF EXISTS `{db_name}`;")
                    conn.exec_driver_sql(f"CREATE DATABASE `{db_name}`;")
                print(f"✅ Database '{db_name}' dropped and recreated successfully.")
        except Exception as e:
            print(f"❌ Failed to drop database: {e}")
            
def drop_table_by_name(app, model_name):
    with app.app_context():
        from models import __all__ as model_list
        try:
            if model_name not in model_list:
                print(f"❌ No model named '{model_name}' found.")
                return
            model_class = getattr(__import__('models'), model_name)
            model_class.__table__.drop(db.engine)
            print(f"✅ Dropped table: {model_name}")
        except Exception as e:
            print(f"❌ Failed to drop {model_name}: {e}")

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
        
