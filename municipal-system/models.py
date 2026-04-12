from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    holding_no = db.Column(db.String(50), nullable=False)
    ward_no = db.Column(db.String(20), nullable=False)
    circle_no = db.Column(db.String(20), nullable=False)
    moholla_name = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120), nullable=False)
    father_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    mobile = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def missing_required_count(self) -> int:
        required = [
            self.holding_no,
            self.ward_no,
            self.circle_no,
            self.moholla_name,
            self.owner_name,
            self.father_name,
        ]
        return sum(1 for item in required if not item or not str(item).strip())
