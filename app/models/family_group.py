"""
Family Group model for managing family prayer groups.

This module defines the FamilyGroup model for creating and managing
family prayer groups with shared prayer tracking and notifications.
"""

from config.database import db
from datetime import datetime
from typing import Dict, Any


class FamilyGroup(db.Model):
    """Model for family prayer groups."""
    
    __tablename__ = 'family_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='family_group_memberships')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert family group member to dictionary."""
        return {
            'id': self.id,
            'family_group_id': self.family_group_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_active': self.is_active,
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<FamilyGroupMember {self.user_id} in group {self.family_group_id}>'
