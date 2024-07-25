import os
import hashlib
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from app import db

class SentImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    image_hash = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f'<SentImage {self.user_id} - {self.image_hash}>'

def __calculate_image_hash(image_path):
    """Calculate the SHA-256 hash of the image."""
    with Image.open(image_path) as img:
        img_bytes = img.tobytes()
        return hashlib.sha256(img_bytes).hexdigest()

def mark_image_as_sent(user_id, image_path):
    if not os.path.exists(image_path):
        return {"error": "Image not found"}, 404

    image_hash = __calculate_image_hash(image_path)

    new_sent_image = SentImage(user_id=user_id, image_hash=image_hash)
    db.session.add(new_sent_image)
    db.session.commit()

    return {"message": "Image marked as sent"}, 201

def grab_first_unsent_media(user_id, image_directory) -> str | None:
    for image_name in os.listdir(image_directory):
        image_path = os.path.join(image_directory, image_name)
        if not has_image_been_sent(user_id, image_path):
            return image_path
    return None

def has_image_been_sent(user_id, image_path):
    if not os.path.exists(image_path):
        return {"error": "Image not found"}, 404

    image_hash = __calculate_image_hash(image_path)

    sent_image = SentImage.query.filter_by(user_id=user_id, image_hash=image_hash).first()
    if sent_image:
        return True

    return False
