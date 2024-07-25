# app.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from config import create_app
from tasks import run_main_with_context
from datetime import datetime, timedelta
import random

app = create_app()

def get_next_run_time():
    """Calculate the next run time with a random minute offset."""
    now = datetime.now()
    random_minute_offset = random.randint(0, 59)
    next_run_time = now + timedelta(hours=1, minutes=random_minute_offset)
    return next_run_time

if __name__ == '__main__':
    # Set up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=lambda: run_main_with_context(app),  # Pass the app instance to the task function
        trigger=IntervalTrigger(hours=1, start_date=get_next_run_time()),
        id='my_task',
        name='Run my_scheduled_task every hour with a random minute offset',
        replace_existing=True)

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True)
