import os
import subprocess
import platform
import sys
import base64
import time
from flask_migrate import init as flask_migrate_init
from flask_migrate import migrate as flask_migrate_migrate
from flask_migrate import upgrade as flask_migrate_upgrade
from models import Admin, db

# === 🛠️ Setup Command ===
def run_setup():
    os_type = platform.system()
    print("📦 Installing Python requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    if os_type == "Linux":
        print("🔧 Installing Node.js & npm for Linux...")
        subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"])
        print("🌐 Initializing Tailwind CSS...")
        subprocess.run(["npm", "init", "-y"])
        subprocess.run(["npm", "install", "-D", "tailwindcss"])
        subprocess.run([
        "npx", "tailwindcss", "-i", "./static/src/input.css",
        "-o", "./static/css/output.css"
    ])

    elif os_type == "Darwin":
        print("🍏 Installing Node.js for macOS...")
        subprocess.run(["brew", "install", "node"])
    elif os_type == "Windows":
        print("🪟 Installing Node.js using Scoop on Windows...")

        env = os.environ.copy()

        # Set execution policy and TLS
        subprocess.run([
            "powershell", "-Command",
            "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; "
            "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12"
        ], check=True, env=env)

        # Install Scoop (if not already installed)
        scoop_shims_path = os.path.expanduser("~/scoop/shims")
        if not os.path.exists(scoop_shims_path):
            subprocess.run([
                "powershell", "-Command",
                "iwr -useb get.scoop.sh | iex"
            ], shell=True, check=True, env=env)
            time.sleep(3)

        # Add scoop shims to PATH for current session
        env["PATH"] = f"{scoop_shims_path};{env['PATH']}"

        # Install Node.js using Scoop
        subprocess.run(["powershell", "-Command", "scoop install nodejs"], check=True, env=env)

        # Add Node.js install path to PATH for current session
        node_path = os.path.expanduser("~/scoop/apps/nodejs/current")
        env["PATH"] = f"{node_path};{env['PATH']}"

        time.sleep(5)
        print("🌐 Initializing Tailwind CSS...")

        # Set up Tailwind CSS
        subprocess.run(["powershell", "-Command", "npm init -y"], check=True, env=env)
        subprocess.run(["powershell", "-Command", "npm install tailwindcss @tailwindcss/cli"], check=True, env=env)
        subprocess.run([
            "powershell", "-Command",
            "npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css"
        ], check=True, env=env)

        print("✅ Node.js and Tailwind CSS installed and configured successfully.")


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
    from flask_migrate import init
    print("Initializing migrations directory...")
    init()
    print("Migration directory initialized.")

def migrate_commit_and_apply():
    from flask_migrate import migrate, upgrade
    print("Generating migration script...")
    migrate()
    commit_msg = input("Enter migration commit message (e.g., 'Added user table'): ").strip()
    if commit_msg:
        # Optionally: write commit message somewhere or log it.
        print(f"Commit message: {commit_msg}")
    else:
        print("No commit message entered.")

    print("Applying migration to database...")
    upgrade()
    print("Migration complete.")

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

def create_admin(email, password):
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
        new_admin = Admin(email=email)
        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()
        print(f"✅ Admin created successfully: {email}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create admin: {e}")
