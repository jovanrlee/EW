import os
from config import db
from datetime import datetime, date
import logging

class SentMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(128), nullable=False)
    media_path = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<SentMedia {self.thread_id} - {self.media_path}>'

def mark_media_as_sent(thread_id, media_path) -> None:
    if not os.path.exists(media_path):
        logging.error(f"Image not found: {media_path}")
        raise Exception("Image not found")

    new_sent_image = SentMedia(thread_id=thread_id, media_path=media_path, timestamp=datetime.now())
    db.session.add(new_sent_image)
    db.session.commit()
    logging.info(f"Marked media {media_path} as sent for thread {thread_id}")

def grab_first_unsent_media(thread_id, media_directory) -> str | None:
    if not os.path.exists(media_directory):
        logging.error(f"Directory not found: {media_directory}")
        raise FileNotFoundError(f"Directory not found: {media_directory}")

    logging.info(f"Scanning directory: {media_directory} for thread {thread_id}")

    for media_name in os.listdir(media_directory):
        media_path = os.path.join(media_directory, media_name)
        if not has_media_been_sent(thread_id, media_path):
            logging.info(f"Found unsent media for thread {thread_id}: {media_path}")
            return media_path
    return None

def has_media_been_sent(thread_id: str, media_path: str) -> bool:
    if not os.path.exists(media_path):
        logging.error(f"Image not found: {media_path}")
        return True  # Assume it's been sent to avoid processing non-existent files

    sent_media = SentMedia.query.filter_by(thread_id=thread_id, media_path=media_path).first()
    if sent_media:
        logging.info(f"Media already sent to thread {thread_id}: {media_path}")
        return True
    return False

def has_been_sent_today_media(thread_id) -> bool:
    today = date.today()
    sent_today = SentMedia.query.filter(
        SentMedia.thread_id == thread_id,
        db.func.date(SentMedia.timestamp) == today
    ).first()
    return bool(sent_today)
