import secrets
import string
from datetime import datetime, timedelta

import pytz
from zoneinfo import ZoneInfo

from config.database import db


class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    verification_code = db.Column(db.String(10), nullable=False)
    verification_type = db.Column(db.String(20), nullable=False)  # 'email_verification', 'password_reset', 'login_otp'
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))

    # Relationships
    user = db.relationship('User', backref='email_verifications')

    @staticmethod
    def generate_verification_code(length=6):
        """Generate a random verification code."""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def create_verification(user_id, email, verification_type, expires_in_minutes=15):
        """Create a new verification record."""
        # Invalidate any existing verification codes for this user and type
        EmailVerification.query.filter_by(
            user_id=user_id,
            verification_type=verification_type,
            is_used=False
        ).update({'is_used': True})

        verification_code = EmailVerification.generate_verification_code()
        expires_at = datetime.now(pytz.UTC) + timedelta(minutes=expires_in_minutes)

        verification = EmailVerification(
            user_id=user_id,
            email=email,
            verification_code=verification_code,
            verification_type=verification_type,
            expires_at=expires_at
        )

        db.session.add(verification)
        db.session.commit()

        return verification

    def is_valid(self):
        """Check if the verification code is still valid."""
        if self.is_used:
            return False

        # Handle timezone comparison - expires_at might be naive when retrieved from DB
        current_time = datetime.now(pytz.UTC)

        if self.expires_at.tzinfo is None:
            # If expires_at is naive, assume it's in UTC and make it timezone-aware
            expires_at_aware = pytz.UTC.localize(self.expires_at)
        else:
            # If expires_at is already timezone-aware, use it as is
            expires_at_aware = self.expires_at

        return current_time < expires_at_aware

    def mark_as_used(self):
        """Mark the verification code as used."""
        self.is_used = True
        db.session.commit()

    def localized_expires_at(self):
        """Return expires_at localized to the user's timezone."""
        if not self.expires_at:
            return None

        # Handle timezone conversion properly
        if self.expires_at.tzinfo is None:
            # If naive, assume UTC and localize
            utc_time = pytz.UTC.localize(self.expires_at)
        else:
            # If already timezone-aware, convert to UTC first
            utc_time = self.expires_at.astimezone(pytz.UTC)

        # Convert to user's timezone
        user_tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return utc_time.astimezone(user_tz)

    def utc_expires_at(self):
        """Return expires_at in UTC."""
        if not self.expires_at:
            return None

        # Handle timezone conversion properly
        if self.expires_at.tzinfo is None:
            # If naive, assume UTC and localize
            return pytz.UTC.localize(self.expires_at)
        # If already timezone-aware, convert to UTC
        return self.expires_at.astimezone(pytz.UTC)

    def localized_created_at(self):
        """Return created_at localized to the user's timezone."""
        if not self.created_at:
            return None

        # Handle timezone conversion properly
        if self.created_at.tzinfo is None:
            # If naive, assume UTC and localize
            utc_time = pytz.UTC.localize(self.created_at)
        else:
            # If already timezone-aware, convert to UTC first
            utc_time = self.created_at.astimezone(pytz.UTC)

        # Convert to user's timezone
        user_tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return utc_time.astimezone(user_tz)

    def utc_created_at(self):
        """Return created_at in UTC."""
        if not self.created_at:
            return None

        # Handle timezone conversion properly
        if self.created_at.tzinfo is None:
            # If naive, assume UTC and localize
            return pytz.UTC.localize(self.created_at)
        # If already timezone-aware, convert to UTC
        return self.created_at.astimezone(pytz.UTC)

    def to_dict(self):
        """Convert verification object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'verification_type': self.verification_type,
            'expires_at': self.localized_expires_at().isoformat() if self.expires_at else None,
            'expires_at_utc': self.utc_expires_at().isoformat() if self.expires_at else None,
            'is_used': self.is_used,
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<EmailVerification {self.verification_type} for {self.email}>'
