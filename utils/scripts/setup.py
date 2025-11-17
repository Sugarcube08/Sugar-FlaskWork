
import os
import sys
import subprocess
import platform
import shutil
import time

try:
    import tomllib  # Python 3.11+
except ImportError:
    print("❌ Python 3.11+ is required for tomllib support.")
    sys.exit(1)


# === Core Utility ===
def run(cmd, shell=True, env=None):
    """Run a shell command with logging and safe error handling."""
    print(f"→ {cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(e)
        sys.exit(1)


# === TOML Loader ===
def load_toml(path="./system.toml"):
    """Load system dependency definitions from TOML."""
    if not os.path.exists(path):
        print(f"❌ Missing {path}. Please create it before running setup.")
        sys.exit(1)
    with open(path, "rb") as f:
        return tomllib.load(f)


# === System Dependency Installer ===
def install_system(deps):
    """Install system-level dependencies dynamically (globally)."""
    os_type = platform.system().lower()
    print(f"🧩 Detected OS: {os_type}")

    system_deps = deps.get("system", {})
    for name, cmd_map in system_deps.items():
        cmd = cmd_map.get(os_type) or cmd_map.get("all")
        if not cmd:
            continue

        # Skip already-installed packages
        if shutil.which(name):
            print(f"✔ {name} already installed.")
            continue

        print(f"🔧 Installing {name} globally...")
        run(cmd)

    # After installation, refresh environment PATH
    refresh_env_path()


# === Ensure uv Installed Globally ===
def ensure_uv():
    """Ensure uv is globally available and accessible."""
    uv_path = shutil.which("uv")
    if uv_path:
        print(f"✔ uv found at {uv_path}")
        return uv_path

    print("⚙️ Installing uv globally...")
    os_type = platform.system().lower()
    if os_type == "linux":
        run("sudo snap install astral-uv")
        # Ensure symlink to /usr/local/bin
        if not shutil.which("uv") and os.path.exists("/snap/bin/uv"):
            try:
                run("sudo ln -sf /snap/bin/uv /usr/local/bin/uv")
            except Exception:
                pass
    elif os_type == "darwin":
        run("brew install astral-sh/uv/uv || brew install uv")
    elif os_type == "windows":
        run("scoop install uv")
    else:
        print("❌ Unsupported OS for automatic uv installation.")
        sys.exit(1)

    refresh_env_path()
    uv_path = shutil.which("uv") or "/usr/local/bin/uv"
    return uv_path


# === Refresh PATH to include global bins ===
def refresh_env_path():
    """Ensure common global binary directories are in PATH."""
    env_paths = [
        "/usr/local/bin",
        "/snap/bin",
        os.path.expanduser("~/scoop/shims"),
        os.path.expanduser("~/AppData/Local/Microsoft/WindowsApps"),
    ]
    current_path = os.environ.get("PATH", "")
    for p in env_paths:
        if os.path.exists(p) and p not in current_path:
            os.environ["PATH"] += f":{p}"


# === Python Dependencies ===
def install_python():
    """Install Python dependencies using `uv sync`."""
    uv_path = ensure_uv()
    print("🐍 Syncing Python dependencies with uv...")
    run(f"{uv_path} sync")


# === Tailwind Base File ===
def ensure_tailwind_input():
    """Ensure Tailwind input file exists."""
    if not os.path.exists("./static/src/input.css"):
        os.makedirs("./static/src", exist_ok=True)
        with open("./static/src/input.css", "w") as f:
            f.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        print("🧩 Created ./static/src/input.css (Tailwind base file).")


# === Build Steps (Post-install) ===
def run_build_steps(deps):
    """Execute post-install build commands."""
    os_type = platform.system().lower()
    for name, cmd_map in deps.get("build", {}).items():
        cmd = cmd_map.get(os_type) or cmd_map.get("all")
        if not cmd:
            continue
        print(f"🏗️ Building {name} assets...")
        run(cmd)


# === Main Setup Runner ===
def setup():
    """Main setup entry point."""
    print("🔧 Starting full environment setup...")
    deps = load_toml()

    install_system(deps)
    install_python()
    ensure_tailwind_input()
    run_build_steps(deps)

    print("\n✅ Setup completed successfully! 🎉")


# === Entrypoint ===
if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error during setup: {e}")
        sys.exit(1)