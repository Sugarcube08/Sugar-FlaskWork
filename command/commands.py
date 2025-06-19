import os
import subprocess
import platform
import sys
import base64
import time

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
        subprocess.run(["npx", "tailwindcss", "init"])
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


def configure_scoop_nodejs_tailwind():
    # Check if the platform is Windows
    if platform.system() != 'Windows':
        print("⚠️ This function is designed for Windows only!")
        return
    
    print("🪟 Configuring Scoop, Node.js, and Tailwind CSS for Windows...")

    # Set up environment variables
    env = os.environ.copy()

    # === Step 1: Install Scoop ===
    try:
        print("📦 Installing Scoop...")
        subprocess.run(["powershell", "-Command", "iwr -useb get.scoop.sh | iex"], check=True)
        print("✅ Scoop installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Error while installing Scoop.")
        return

    # === Step 2: Update PATH for Scoop ===
    scoop_shims_path = os.path.expanduser('~/scoop/shims')
    if os.path.exists(scoop_shims_path):
        env['PATH'] = f"{scoop_shims_path};{env['PATH']}"
    else:
        print("⚠️ Scoop shims directory not found, skipping PATH update.")
        return

    # === Step 3: Install Node.js using Scoop ===
    try:
        print("🪟 Installing Node.js using Scoop...")
        subprocess.run(["powershell", "-Command", "scoop install nodejs"], check=True, env=env)
        print("✅ Node.js installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Error while installing Node.js.")
        return

    # Update the PATH for Node.js binaries (typically under scoop/apps/nodejs/current)
    nodejs_path = os.path.expanduser('~/scoop/apps/nodejs/current/bin')
    if os.path.exists(nodejs_path):
        env['PATH'] = f"{nodejs_path};{env['PATH']}"
    else:
        print("⚠️ Node.js directory not found, skipping PATH update.")
        return

    # === Step 4: Install Tailwind CSS using npm ===
    try:
        print("🌐 Initializing Tailwind CSS...")
        subprocess.run(["powershell", "-Command", "npm init -y"], check=True, env=env)
        subprocess.run(["powershell", "-Command", "npm install tailwindcss @tailwindcss/cli"], check=True, env=env)
        subprocess.run(["powershell", "-Command", "npx tailwindcss init"], check=True, env=env)
        subprocess.run([
            "powershell", "-Command",
            "npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css"
        ], check=True, env=env)
        print("✅ Tailwind CSS initialized successfully.")
    except subprocess.CalledProcessError:
        print("❌ Error while installing Tailwind CSS.")
        return


def create_controller(name):
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
    content = template.replace('{className}', class_name).replace('{name}', name.lower())

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
