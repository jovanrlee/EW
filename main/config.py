# config.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure the SQLite database, relative to the app instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the SQLAlchemy db instance
    db.init_app(app)

    # Import the models here to register them with SQLAlchemy
    with app.app_context():
        db.create_all()

    return app
