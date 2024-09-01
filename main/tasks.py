# tasks.py
from config import create_app
from main import main
from config import db
def run_main_with_context(app):
    with app.app_context():
        main()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        main()
