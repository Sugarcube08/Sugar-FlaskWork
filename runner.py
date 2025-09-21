from app_factory import create_app
from models import db  
import os
from route import web
from dotenv import load_dotenv
import argparse
from command.commands import (
    run_setup,
    generate_env,
    create_controller,
    create_model,
    migrate_init,
    migrate_commit_and_apply,
    create_html_template,
    create_all,
    create_component_template,
    create_subtemplate,
    create_admin,
    drop_all_tables,
    drop_table_by_name,
    start_tailwind_watch
)

load_dotenv()

def cli():
    parser = argparse.ArgumentParser(
        description="🛠️ Flask Application Manager",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    subparsers.add_parser("setup", help="Install Python and Tailwind dependencies")

    parser_env = subparsers.add_parser("create:env", help="Generate a secure .env file with SECRET_KEY")
    parser_env.add_argument('--force', action='store_true', help='Force overwrite existing .env file')

    parser_run = subparsers.add_parser("runserver", help="Start the Flask web server")
    parser_run.add_argument('--host', default=os.getenv("HOST"), help='Set the host address (default: 127.0.0.1)')
    parser_run.add_argument('--port', type=int, default=os.getenv("PORT"), help='Set the port number (default: 5000)')

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
    parser_admin.add_argument("post", help="Admin post (default: Core Member)", nargs='?', default="Core Member")

    subparsers.add_parser("migrate:init", help="Initialize migration directory")
    subparsers.add_parser("migrate", help="Generate migration script and upgrade DB")
    
    parser_drop = subparsers.add_parser("migrate:drop", help="Drop tables from the database")
    parser_drop.add_argument("target", help="'all' or model name (e.g., Admin, User)")

    args = parser.parse_args()

    if args.command == "setup":
        print("🔧 Running setup...")
        run_setup()

    elif args.command == "create:env":
        print("🔐 Generating .env file...")
        generate_env(force=args.force)

    elif args.command == "runserver":
        app = create_app()
        with app.app_context():
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
        app = create_app()
        with app.app_context():
            migrate_init()

    elif args.command == "migrate":
        app = create_app()
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
        app = create_app()
        with app.app_context():
            create_admin(args.email, args.password, args.post)
            
    elif args.command == "migrate:drop":
        app = create_app()
        with app.app_context():
            if args.target.lower() == "all":
                drop_all_tables(app)
            else:
                drop_table_by_name(app, args.target)

    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
