from datetime import datetime

import pytz
from werkzeug.security import check_password_hash, generate_password_hash
from zoneinfo import ZoneInfo

from config.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    fiqh_method = db.Column(db.String(20), default='shafi')  # shafi, hanafi, maliki, hanbali
    language = db.Column(db.String(10), default='en')  # ar, en
    notification_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    reminder_times = db.Column(db.JSON, default=lambda: {
        'fajr': 15, 'dhuhr': 10, 'asr': 10, 'maghrib': 5, 'isha': 10
    })  # Minutes before prayer time
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    # Relationships
    prayer_completions = db.relationship('PrayerCompletion', backref='user', lazy=True, cascade='all, delete-orphan')
    family_members = db.relationship('FamilyMember', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)

    def localized_created_at(self):
        """Return created_at localized to the user's timezone."""
        if not self.created_at:
            return None
        tz = ZoneInfo(self.timezone or 'UTC')
        return self.created_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_created_at(self):
        """Return created_at in UTC."""
        if not self.created_at:
            return None
        return self.created_at.replace(tzinfo=ZoneInfo('UTC'))

    def localized_updated_at(self):
        """Return updated_at localized to the user's timezone."""
        if not self.updated_at:
            return None
        tz = ZoneInfo(self.timezone or 'UTC')
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_updated_at(self):
        """Return updated_at in UTC."""
        if not self.updated_at:
            return None
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'location_lat': self.location_lat,
            'location_lng': self.location_lng,
            'timezone': self.timezone,
            'city': self.city,
            'country': self.country,
            'fiqh_method': self.fiqh_method,
            'language': self.language,
            'notification_enabled': self.notification_enabled,
            'email_notifications': self.email_notifications,
            'reminder_times': self.reminder_times,
            'email_verified': self.email_verified,
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None,
            'updated_at': self.localized_updated_at().isoformat() if self.updated_at else None,
            'updated_at_utc': self.utc_updated_at().isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
