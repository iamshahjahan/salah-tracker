"""
Email service for sending verification codes, OTPs, and password reset links.

This service handles all email-related functionality including sending verification
codes for email verification, OTPs for login, and password reset links.
"""

from typing import Dict, Any, Optional
from flask import current_app, url_for
from flask_mail import Message
from datetime import datetime

from .base_service import BaseService
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.config.settings import Config


class EmailService(BaseService):
    """
    Service for handling email operations.

    This service provides methods for sending verification codes, OTPs,
    and password reset links with proper email templates and error handling.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the email service.

        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        # Use Flask app config for mail settings
        self.mail_config = {
            'server': current_app.config.get('MAIL_SERVER'),
            'port': current_app.config.get('MAIL_PORT'),
            'username': current_app.config.get('MAIL_USERNAME'),
            'password': current_app.config.get('MAIL_PASSWORD'),
            'use_tls': current_app.config.get('MAIL_USE_TLS', True)
        }

    def send_email_verification(self, user: User) -> Dict[str, Any]:
        """
        Send email verification code to user.

        Args:
            user: User instance to send verification to.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Create verification code
            verification = EmailVerification.create_verification(
                user_id=user.id,
                email=user.email,
                verification_type='email_verification',
                expires_in_minutes=30  # 30 minutes for email verification
            )

            # Send email
            subject = "Verify Your Email - SalahTracker"
            template = self._get_email_verification_template(user, verification.verification_code)

            success = self._send_email(user.email, subject, template)

            if success:
                self.logger.info(f"Email verification sent to {user.email}")
                return {
                    'success': True,
                    'message': 'Verification code sent to your email',
                    'verification_id': verification.id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send verification email'
                }

        except Exception as e:
            return self.handle_service_error(e, 'send_email_verification')

    def send_login_otp(self, user: User) -> Dict[str, Any]:
        """
        Send OTP for login to user.

        Args:
            user: User instance to send OTP to.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Create OTP
            verification = EmailVerification.create_verification(
                user_id=user.id,
                email=user.email,
                verification_type='login_otp',
                expires_in_minutes=10  # 10 minutes for login OTP
            )

            # Send email
            subject = "Your Login Code - SalahTracker"
            template = self._get_login_otp_template(user, verification.verification_code)

            success = self._send_email(user.email, subject, template)

            if success:
                self.logger.info(f"Login OTP sent to {user.email}")
                return {
                    'success': True,
                    'message': 'Login code sent to your email',
                    'verification_id': verification.id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send login code'
                }

        except Exception as e:
            return self.handle_service_error(e, 'send_login_otp')

    def send_password_reset(self, user: User) -> Dict[str, Any]:
        """
        Send password reset link to user.

        Args:
            user: User instance to send reset link to.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Create password reset verification
            verification = EmailVerification.create_verification(
                user_id=user.id,
                email=user.email,
                verification_type='password_reset',
                expires_in_minutes=60  # 1 hour for password reset
            )

            # Generate reset link
            reset_link = self._generate_password_reset_link(verification.verification_code)

            # Send email
            subject = "Reset Your Password - SalahTracker"
            template = self._get_password_reset_template(user, reset_link)

            success = self._send_email(user.email, subject, template)

            if success:
                self.logger.info(f"Password reset link sent to {user.email}")
                return {
                    'success': True,
                    'message': 'Password reset link sent to your email'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send password reset email'
                }

        except Exception as e:
            return self.handle_service_error(e, 'send_password_reset')

    def verify_code(self, email: str, code: str, verification_type: str) -> Dict[str, Any]:
        """
        Verify a verification code.

        Args:
            email: User's email address.
            code: Verification code to verify.
            verification_type: Type of verification ('email_verification', 'login_otp', 'password_reset').

        Returns:
            Dict[str, Any]: Verification result with success status or error.
        """
        try:
            # Find the verification record
            verification = EmailVerification.query.filter_by(
                email=email,
                verification_code=code,
                verification_type=verification_type,
                is_used=False
            ).first()

            if not verification:
                return {
                    'success': False,
                    'error': 'Invalid verification code'
                }

            if not verification.is_valid():
                return {
                    'success': False,
                    'error': 'Verification code has expired'
                }

            # Mark as used
            verification.mark_as_used()

            # Get user
            user = User.query.get(verification.user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Update user based on verification type
            if verification_type == 'email_verification':
                user.email_verified = True
                self.db_session.commit()

            self.logger.info(f"Verification successful for {email} - {verification_type}")

            return {
                'success': True,
                'message': 'Verification successful',
                'user': user.to_dict()
            }

        except Exception as e:
            return self.handle_service_error(e, 'verify_code')

    def _send_email(self, to_email: str, subject: str, template: str) -> bool:
        """
        Send email using Flask-Mail.

        Args:
            to_email: Recipient email address.
            subject: Email subject.
            template: Email template content.

        Returns:
            bool: True if email sent successfully, False otherwise.
        """
        try:
            if not self.mail_config:
                self.logger.warning("Mail configuration not available")
                return False

            msg = Message(
                subject=subject,
                sender=self.mail_config['username'],
                recipients=[to_email]
            )
            msg.html = template

            from mail_config import mail
            mail.send(msg)
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def _get_email_verification_template(self, user: User, code: str) -> str:
        """Get email verification template."""
        return f"""
Assalamu Alaikum {user.first_name},

Welcome to SalahTracker! Please verify your email address to complete your registration.

Your verification code is: {code}

This code will expire in 30 minutes.

If you didn't create an account with SalahTracker, please ignore this email.

May Allah bless you and accept your prayers.

Best regards,
SalahTracker Team
        """.strip()

    def _get_login_otp_template(self, user: User, code: str) -> str:
        """Get login OTP template."""
        return f"""
Assalamu Alaikum {user.first_name},

You requested a login code for your SalahTracker account.

Your login code is: {code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email and consider changing your password.

May Allah bless you and accept your prayers.

Best regards,
SalahTracker Team
        """.strip()

    def _get_password_reset_template(self, user: User, reset_link: str) -> str:
        """Get password reset template."""
        return f"""
Assalamu Alaikum {user.first_name},

You requested to reset your password for your SalahTracker account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

May Allah bless you and accept your prayers.

Best regards,
SalahTracker Team
        """.strip()

    def _generate_password_reset_link(self, code: str) -> str:
        """Generate password reset link."""
        # In a real application, you would use the actual domain
        # For now, we'll use a placeholder that the frontend can handle
        base_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5001')
        return f"{base_url}/reset-password?code={code}"
