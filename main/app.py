from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from main import main #tasks
from datetime import datetime, timedelta
import random


app = Flask(__name__)

# Configure the SQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)


# @app.route('/')
# def hello():
#     return '<h1>Hello, World!</h1>'

def get_next_run_time():
    """Calculate the next run time with a random minute offset."""
    now = datetime.now()
    random_minute_offset = random.randint(0, 59)
    next_run_time = now + timedelta(hours=1, minutes=random_minute_offset)
    return next_run_time

if __name__ == '__main__':
    # Create the database and the tables
    with app.app_context():
        db.create_all()

    # Set up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=main, # Run this every 
        trigger=IntervalTrigger(hours=1, start_date=get_next_run_time),
        id='my_task',
        name='Run my_scheduled_task every minute',
        replace_existing=True)

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True)