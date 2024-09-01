
import os
from config import db
from datetime import datetime, date
import logging

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    session_id = db.Column(db.String, nullable=True) # TODO change to JSON


def create_user():
    pass

def delete_user():
    pass
