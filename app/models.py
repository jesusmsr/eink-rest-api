from . import db
from datetime import datetime

class DisplayRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pending = db.Column(db.Boolean, default=True)
    was_sent = db.Column(db.Boolean, default=False)
    last_sent_at = db.Column(db.DateTime, nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "image_path": self.image_path,
            "timestamp": self.timestamp.isoformat()
        }

class BatteryStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voltage = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
