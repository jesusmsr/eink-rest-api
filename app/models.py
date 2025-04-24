from . import db
from datetime import datetime

class DisplayRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BatteryStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voltage = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
