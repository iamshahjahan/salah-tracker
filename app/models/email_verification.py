from database import db
from datetime import datetime, timedelta
import secrets
import string

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    verification_code = db.Column(db.String(10), nullable=False)
    verification_type = db.Column(db.String(20), nullable=False)  # 'email_verification', 'password_reset', 'login_otp'
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='email_verifications')

    @staticmethod
    def generate_verification_code(length=6):
        """Generate a random verification code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def create_verification(user_id, email, verification_type, expires_in_minutes=15):
        """Create a new verification record"""
        # Invalidate any existing verification codes for this user and type
        EmailVerification.query.filter_by(
            user_id=user_id,
            verification_type=verification_type,
            is_used=False
        ).update({'is_used': True})

        verification_code = EmailVerification.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

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
        """Check if the verification code is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at

    def mark_as_used(self):
        """Mark the verification code as used"""
        self.is_used = True
        db.session.commit()

    def to_dict(self):
        """Convert verification object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'verification_type': self.verification_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<EmailVerification {self.verification_type} for {self.email}>'
