# tasks.py
from config import create_app
from main import main

def run_main_with_context(app):
    with app.app_context():
        main()

if __name__ == "__main__":
    app = create_app()
    run_main_with_context(app)
