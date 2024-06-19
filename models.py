from extensions import db
from datetime import datetime

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Image {self.filename}>'