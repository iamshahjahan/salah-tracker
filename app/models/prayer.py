from datetime import datetime
from enum import Enum

import pytz
from zoneinfo import ZoneInfo

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
    FUTURE = "future"
    ONGOING = "ongoing"
    MISSED = "missed"


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

    # Keep date + time separate, but store in UTC
    prayer_date = db.Column(db.Date, nullable=False)
    prayer_time = db.Column(db.Time, nullable=False)

    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)

    # Store timezone string (IANA identifier, e.g. "Asia/Kolkata")
    timezone = db.Column(db.String(50), default='UTC')

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))

    # Relationships
    user = db.relationship('User', backref='prayers')

    def localized_prayer_datetime(self):
        """Return prayer datetime localized to the stored timezone."""
        naive_dt = datetime.combine(self.prayer_date, self.prayer_time)
        tz = ZoneInfo(self.timezone or 'UTC')
        return naive_dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_prayer_datetime(self):
        """Return prayer datetime in UTC."""
        naive_dt = datetime.combine(self.prayer_date, self.prayer_time)
        return naive_dt.replace(tzinfo=ZoneInfo('UTC'))

    def localized_created_at(self):
        """Return created_at localized to the stored timezone."""
        if not self.created_at:
            return None
        tz = ZoneInfo(self.timezone or 'UTC')
        return self.created_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_created_at(self):
        """Return created_at in UTC."""
        if not self.created_at:
            return None
        return self.created_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self):
        """Convert prayer object to dictionary with timezone-aware datetimes."""
        return {
            'id': self.id,
            'prayer_type': self.prayer_type.value,
            'prayer_date': self.prayer_date.isoformat(),
            'prayer_time': self.prayer_time.strftime('%H:%M'),
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'timezone': self.timezone,
            'prayer_datetime_local': self.localized_prayer_datetime().isoformat(),
            'prayer_datetime_utc': self.utc_prayer_datetime().isoformat(),
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Prayer {self.prayer_type.value} on {self.prayer_date}>'


class PrayerCompletion(db.Model):
    __tablename__ = 'prayer_completions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prayer_id = db.Column(db.Integer, db.ForeignKey('prayers.id'), nullable=False)
    marked_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(pytz.UTC))  # store in UTC
    status = db.Column(db.Enum(PrayerCompletionStatus), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    prayer = db.relationship('Prayer', backref='completions')

    def localized_marked_at(self):
        """Return marked_at localized to the prayer's timezone."""
        if not self.marked_at:
            return None
        tz = ZoneInfo(self.prayer.timezone if self.prayer else 'UTC')
        return self.marked_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_marked_at(self):
        """Return marked_at in UTC."""
        if not self.marked_at:
            return None
        return self.marked_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self):
        """Convert prayer completion object to dictionary with timezone-aware datetime."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prayer_id': self.prayer_id,
            'marked_at': self.localized_marked_at().isoformat() if self.marked_at else None,
            'marked_at_utc': self.utc_marked_at().isoformat() if self.marked_at else None,
            'status': self.status.value if self.status else None,
            'notes': self.notes,
            'prayer': self.prayer.to_dict() if self.prayer else None
        }

    def __repr__(self):
        return f'<PrayerCompletion user_id={self.user_id} prayer_id={self.prayer_id}>'
