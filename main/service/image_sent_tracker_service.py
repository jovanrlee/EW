import os
from app import db
from datetime import datetime,date


class SentMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, nullable=False)
    media_path = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<SentMedia {self.thread_id} - {self.media_path}>'

def mark_media_as_sent(thread_id, media_path):
    if not os.path.exists(media_path):
        return {"error": "Media not found"}, 404

    new_sent_image = SentMedia(thread_id=thread_id, media_path=media_path, timestamp=datetime.now())
    db.session.add(new_sent_image)
    db.session.commit()

    return {"message": "Media marked as sent"}, 201

def grab_first_unsent_media(thread_id, media_directory) -> str | None:
    for media_name in os.listdir(media_directory):
        media_path = os.path.join(media_directory, media_name)
        if not has_media_been_sent(thread_id, media_path):
            return media_path
    return None

def has_media_been_sent(thread_id, image_path):
    if not os.path.exists(image_path):
        return {"error": "Image not found"}, 404
    
    sent_media = SentMedia.query.filter_by(thread_id=thread_id, media_path=image_path).first()
    if sent_media:
        return True
    return False

def has_been_sent_today_media() -> bool:
    today = date.today()
    sent_today = SentMedia.query.filter(db.func.date(SentMedia.timestamp) == today).first()
    return bool(sent_today)
