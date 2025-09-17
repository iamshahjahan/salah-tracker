"""Family Group model for managing family prayer groups.

This module defines the FamilyGroup model for creating and managing
family prayer groups with shared prayer tracking and notifications.
"""

from datetime import datetime
from typing import Any, Dict

import pytz
from zoneinfo import ZoneInfo

from config.database import db


class FamilyGroup(db.Model):
    """Model for family prayer groups."""

    __tablename__ = 'family_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    # Relationships
    admin_user = db.relationship('User', backref='administered_groups', foreign_keys=[admin_user_id])
    members = db.relationship('FamilyGroupMember', backref='family_group', lazy=True, cascade='all, delete-orphan')

    def generate_invite_code(self) -> str:
        """Generate a unique invite code for the family group."""
        import random
        import string

        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not FamilyGroup.query.filter_by(invite_code=code).first():
                self.invite_code = code
                return code

    def localized_created_at(self):
        """Return created_at localized to the admin user's timezone."""
        if not self.created_at:
            return None
        tz = ZoneInfo(self.admin_user.timezone if self.admin_user else 'UTC')
        return self.created_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_created_at(self):
        """Return created_at in UTC."""
        if not self.created_at:
            return None
        return self.created_at.replace(tzinfo=ZoneInfo('UTC'))

    def localized_updated_at(self):
        """Return updated_at localized to the admin user's timezone."""
        if not self.updated_at:
            return None
        tz = ZoneInfo(self.admin_user.timezone if self.admin_user else 'UTC')
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_updated_at(self):
        """Return updated_at in UTC."""
        if not self.updated_at:
            return None
        return self.updated_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert family group to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'admin_user_id': self.admin_user_id,
            'invite_code': self.invite_code,
            'is_active': self.is_active,
            'member_count': len(self.members),
            'created_at': self.localized_created_at().isoformat() if self.created_at else None,
            'created_at_utc': self.utc_created_at().isoformat() if self.created_at else None,
            'updated_at': self.localized_updated_at().isoformat() if self.updated_at else None,
            'updated_at_utc': self.utc_updated_at().isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<FamilyGroup {self.name}>'


class FamilyGroupMember(db.Model):
    """Model for family group members."""

    __tablename__ = 'family_group_members'

    id = db.Column(db.Integer, primary_key=True)
    family_group_id = db.Column(db.Integer, db.ForeignKey('family_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # member, admin
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.UTC))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', backref='family_group_memberships')

    def localized_joined_at(self):
        """Return joined_at localized to the user's timezone."""
        if not self.joined_at:
            return None
        tz = ZoneInfo(self.user.timezone if self.user else 'UTC')
        return self.joined_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)

    def utc_joined_at(self):
        """Return joined_at in UTC."""
        if not self.joined_at:
            return None
        return self.joined_at.replace(tzinfo=ZoneInfo('UTC'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert family group member to dictionary."""
        return {
            'id': self.id,
            'family_group_id': self.family_group_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.localized_joined_at().isoformat() if self.joined_at else None,
            'joined_at_utc': self.utc_joined_at().isoformat() if self.joined_at else None,
            'is_active': self.is_active,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        return f'<FamilyGroupMember {self.user_id} in group {self.family_group_id}>'
