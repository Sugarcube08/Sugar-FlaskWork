# Sugar-Flaskwork

**Sugar-Flaskwork** is a sweet and powerful microframework built on top of Flask, designed for rapid full-stack web development. It combines Flask’s flexibility with modern tools like TailwindCSS, CLI-powered automation, modular MVC architecture, and secure environment setup — all with cross-platform support.

---

## 🚧 Project Status: Under Development

This framework is still in its early phase and evolving rapidly. While many core features are already functional, **your contributions, ideas, and feedback are highly welcome**! If you’re passionate about Python, Flask, or developer tooling — come build with us! 💻✨

---

## ✨ Key Features

- 🔧 **CLI-Driven Development**  
  Built-in command-line interface using `argparse` to scaffold components like:
  - `setup` – install dependencies for Python & Node.js
  - `env:generate` – generate secure `.env` with `SECRET_KEY`
  - `create:controller` – auto-generate controller files from templates
  - `runserver` – run the development server with TailwindCSS live build

- 🌐 **Cross-Platform Support**  
  Compatible with **Linux**, **macOS**, and **Windows**. On Windows, it uses **Scoop** to manage Node.js and TailwindCSS.

- 🎨 **Tailwind CSS Integration**  
  TailwindCSS is initialized and auto-configured during setup, and runs in `--watch` mode when the server starts.

- 🔐 **Secure .env Management**  
  Generates `.env` from a template with base64-encoded cryptographic `SECRET_KEY` using Python's `secrets`, `Fernet`, and `itsdangerous`.

- 🧱 **MVC Structure (in progress)**  
  - `controllers/` – for route logic
  - `models/` – for database models
  - `templates/` – for HTML views
  *(Auto-generation for model and template files is in active development)*

- 📦 **Automated Setup Script**  
  The `setup` command installs all Python and Node dependencies, initializes Tailwind, and prepares the environment.

---

## 🖥️ CLI Commands

```bash
# 🔧 Install all required dependencies (Python & Node)
python app.py setup

# 🔐 Generate a secure .env file with SECRET_KEY
python app.py env:generate

# 📂 Generate a new controller from template
python app.py create:controller -c auth

# 🚀 Run the development server with Tailwind CSS in watch mode
python app.py runserver
```

---

## 🤝 Contributing

**Sugar-Flaskwork is open for contributions!**

Whether you're a student, a Flask developer, or just curious — we’d love your help. Here’s how you can contribute:

* 🚀 Suggest features or improvements
* 🐛 Report bugs or inconsistencies
* ✨ Help build the admin panel or auth system
* 🧪 Write tests or enhance CLI commands
* 📚 Improve the documentation

> To get started, fork this repository and open a pull request.
> Feel free to open an issue for discussion before starting a big change!

---

## 🧃 Credits

Built with ❤️ by [SugarCube](https://github.com/Sugarcube08), powered by Flask and TailwindCSS.
Special thanks to contributors and the Python open-source community!

---

## 📜 License

This project will be licensed under the **MIT License** (to be added).

---

## ☕ Support Me

If you like this project, consider buying me a coffee!
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support%20Me-orange?style=flat-square&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/sugarcube08)

---

## Don't Forget To Subscribe
### Click on the Following Buttons:
[![YouTube Banner](https://img.shields.io/badge/YouTube-%23FF0000.svg?logo=YouTube&logoColor=white)](https://www.youtube.com/@SugarCode-Z?sub_confirmation=1)
[![Instagram Banner](https://img.shields.io/badge/Instagram-%23E4405F.svg?logo=Instagram&logoColor=white)](https://www.instagram.com/sugarcodez)
[![WhatsApp Banner](https://img.shields.io/badge/WhatsApp-%25D366.svg?logo=whatsapp&logoColor=white)](https://whatsapp.com/channel/0029Vb5fFdzKgsNlaxFmhg1T)

---

> 🛠️ **Sugar-Flaskwork** – Build modern Flask apps with speed, structure, and sweetness.
