from datetime import datetime

import pytz
from zoneinfo import ZoneInfo

from config.database import db


class FamilyMember(db.Model):
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    relationship = db.Column(db.String(50), nullable=False)  # e.g., 'spouse', 'child', 'parent', 'friend'
    reminder_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

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

    def localized_updated_at(self):
        """Return updated_at localized to the user's timezone."""
        if not self.updated_at:
            return None
        tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_updated_at(self):
        """Return updated_at in UTC."""
        if not self.updated_at:
            return None
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self):
        """Convert family member object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'relationship': self.relationship,
            'reminder_enabled': self.reminder_enabled,
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None,
            'updated_at': self.localized_updated_at().isoformat() if self.updated_at else None,
            'updated_at_utc': self.utc_updated_at().isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<FamilyMember {self.name} ({self.relationship})>'
