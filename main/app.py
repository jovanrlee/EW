# app.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from config import create_app
from tasks import run_main_with_context
from datetime import datetime, timedelta
import random
from config import db

app = create_app()

def get_next_run_time():
    """Calculate the next run time with a random minute offset."""
    now = datetime.now()
    random_hour_offset = random.randint(1,4)
    random_minute_offset = random.randint(0, 59)
    random_second_offset = random.randint(0, 59)

    next_run_time = now + timedelta(hours=random_hour_offset, minutes=random_minute_offset,seconds=random_second_offset)
    return next_run_time

if __name__ == '__main__':

    with app.app_context():
        db.drop_all()
        db.create_all()
        # TODO run every 4 hour



        # TODO run for 10 minutes every 4 hours
        # Set up the scheduler
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(
            func=lambda: run_main_with_context(app),  # Pass the app instance to the task function
            trigger=IntervalTrigger(start_date=get_next_run_time()),
            id='my_task',
            name='Run my_scheduled_task every hour with a random minute offset',
            replace_existing=True)

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

        app.run(debug=True)
