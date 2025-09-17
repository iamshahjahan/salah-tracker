"""Prayer notification model for managing prayer reminders.

This module defines models for storing and managing prayer notifications,
including email reminders and completion tracking via links.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

import pytz
from zoneinfo import ZoneInfo

from config.database import db


class PrayerNotification(db.Model):
    """Model for prayer notifications."""

    __tablename__ = 'prayer_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prayer_type = db.Column(db.String(20), nullable=False)  # fajr, dhuhr, asr, maghrib, isha
    prayer_date = db.Column(db.Date, nullable=False)
    notification_type = db.Column(db.String(20), default='reminder')  # reminder, completion_link
    sent_at = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(pytz.UTC))
    completed_via_link = db.Column(db.Boolean, default=False)
    completion_link_id = db.Column(db.String(36), nullable=True)  # UUID for completion links
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))

    # Relationships
    user = db.relationship('User', backref='prayer_notifications')

    def generate_completion_link_id(self) -> str:
        """Generate a unique completion link ID."""
        link_id = str(uuid.uuid4())
        self.completion_link_id = link_id
        return link_id

    def get_completion_link(self, base_url: str) -> str:
        """Get the completion link for this notification."""
        if not self.completion_link_id:
            self.generate_completion_link_id()
            db.session.commit()

        return f"{base_url}/complete-prayer/{self.completion_link_id}"

    def is_completion_link_valid(self) -> bool:
        """Check if the completion link is still valid (within 2 hours of creation)."""
        if not self.completion_link_id or self.completed_via_link:
            return False

        # Link is valid for 2 hours after creation
        valid_until = self.created_at + timedelta(hours=2)
        return datetime.now(pytz.UTC) <= valid_until

    def localized_sent_at(self):
        """Return sent_at localized to the user's timezone."""
        if not self.sent_at:
            return None
        tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return self.sent_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_sent_at(self):
        """Return sent_at in UTC."""
        if not self.sent_at:
            return None
        return self.sent_at.replace(tzinfo=ZoneInfo('UTC'))

    def localized_created_at(self):
        """Return created_at localized to the user's timezone."""
        if not self.created_at:
            return None
        tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return self.created_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_created_at(self):
        """Return created_at in UTC."""
        if not self.created_at:
            return None
        return self.created_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert prayer notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prayer_type': self.prayer_type,
            'prayer_date': self.prayer_date.isoformat() if self.prayer_date else None,
            'notification_type': self.notification_type,
            'sent_at': self.localized_sent_at().isoformat() if self.sent_at else None,
            'sent_at_utc': self.utc_sent_at().isoformat() if self.sent_at else None,
            'completed_via_link': self.completed_via_link,
            'completion_link_id': self.completion_link_id,
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<PrayerNotification {self.prayer_type} for user {self.user_id} on {self.prayer_date}>'
