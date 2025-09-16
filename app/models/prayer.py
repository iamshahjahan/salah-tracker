from datetime import datetime
from enum import Enum

from config.database import db


class PrayerType(Enum):
    FAJR = "fajr"
    DHUHR = "dhuhr"
    ASR = "asr"
    MAGHRIB = "maghrib"
    ISHA = "isha"
    ZAKAAT = "zakaat"
    JUMMAH = "jummah"
    FASTING = "fasting"
    QURAN_TILAWAT = "quran_tilawat"
    HAJJ = "Hajj"

class PrayerStatus(Enum):
    FUTURE = "future"  # Before prayer start time
    ONGOING = "ongoing"  # Time is between prayer's start and end
    MISSED = "missed"  # After prayer end time, can be moved to qada


class PrayerCompletionStatus(Enum):
    JAMAAT = "jamaat"
    WITHOUT_JAMAAT = "without_jamaat"
    MISSED = "missed"
    QADA = "qada"


class Prayer(db.Model):
    __tablename__ = 'prayers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prayer_type = db.Column(db.Enum(PrayerType), nullable=False)
    prayer_date = db.Column(db.Date, nullable=False)
    prayer_time = db.Column(db.Time, nullable=False)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='prayers')

    def to_dict(self):
        """Convert prayer object to dictionary."""
        return {
            'id': self.id,
            'prayer_type': self.prayer_type.value,
            'prayer_date': self.prayer_date.isoformat(),
            'prayer_time': self.prayer_time.strftime('%H:%M'),
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Prayer {self.prayer_type.value} on {self.prayer_date}>'

class PrayerCompletion(db.Model):
    __tablename__ = 'prayer_completions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prayer_id = db.Column(db.Integer, db.ForeignKey('prayers.id'), nullable=False)
    marked_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(PrayerCompletionStatus), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    prayer = db.relationship('Prayer', backref='completions')

    def to_dict(self):
        """Convert prayer completion object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prayer_id': self.prayer_id,
            'marked_at': self.marked_at.isoformat() if self.marked_at else None,
            'status': self.status.value if self.status else None,
            'notes': self.notes,
            'prayer': self.prayer.to_dict() if self.prayer else None
        }

    def __repr__(self):
        return f'<PrayerCompletion user_id={self.user_id} prayer_id={self.prayer_id}>'
