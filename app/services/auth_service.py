"""
Authentication service for user management and JWT token handling.

This service handles user authentication, registration, and JWT token management
with proper validation and security measures.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

from .base_service import BaseService
from .email_service import EmailService
from app.models.user import User
from app.models.email_verification import EmailVerification
from app.config.settings import Config


class AuthService(BaseService):
    """
    Service for handling user authentication and authorization.

    This service provides methods for user registration, login, password validation,
    and JWT token management with proper security measures.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the authentication service.

        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        # Use Flask app config for JWT settings
        self.jwt_secret = current_app.config.get('JWT_SECRET_KEY', 'default-secret')
        self.jwt_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(days=30))
        self.email_service = EmailService(config)

    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user with validation and password hashing.

        Args:
            user_data: Dictionary containing user registration data including:
                - username: User's email/username
                - email: User's email address
                - password: Plain text password
                - first_name: User's first name
                - last_name: User's last name
                - phone_number: User's phone number
                - location_lat: User's latitude
                - location_lng: User's longitude
                - timezone: User's timezone

        Returns:
            Dict[str, Any]: Registration result with success status and user data or error.
        """
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not user_data.get(field):
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }

            # Check if user already exists
            existing_user = self._get_user_by_email(user_data['email'])
            if existing_user:
                return {
                    'success': False,
                    'error': 'User with this email already exists'
                }

            # Hash password
            password_hash = generate_password_hash(user_data['password'])

            # Create user record
            user = self.create_record(
                User,
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone_number=user_data.get('phone_number'),
                location_lat=user_data.get('location_lat'),
                location_lng=user_data.get('location_lng'),
                timezone=user_data.get('timezone', self.config.DEFAULT_TIMEZONE),
                notification_enabled=user_data.get('notification_enabled', True)
            )

            self.logger.info(f"User registered successfully: {user.email}")

            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'User registered successfully'
            }

        except Exception as e:
            return self.handle_service_error(e, 'user_registration')

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email address.
            password: Plain text password.

        Returns:
            Dict[str, Any]: Authentication result with success status, user data, and tokens or error.
        """
        try:
            # Get user by email
            user = self._get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }

            # Verify password
            if not check_password_hash(user.password_hash, password):
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }

            # Generate tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)

            self.logger.info(f"User authenticated successfully: {user.email}")

            return {
                'success': True,
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'Authentication successful'
            }

        except Exception as e:
            return self.handle_service_error(e, 'user_authentication')

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Generate a new access token using a valid refresh token.

        Args:
            refresh_token: Valid refresh token.

        Returns:
            Dict[str, Any]: Token refresh result with new access token or error.
        """
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token,
                self.jwt_secret,
                algorithms=['HS256']
            )

            user_id = payload.get('user_id')
            if not user_id:
                return {
                    'success': False,
                    'error': 'Invalid refresh token'
                }

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Generate new access token
            new_access_token = self._generate_access_token(user)

            return {
                'success': True,
                'access_token': new_access_token,
                'message': 'Token refreshed successfully'
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Refresh token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid refresh token'
            }
        except Exception as e:
            return self.handle_service_error(e, 'token_refresh')

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a JWT access token.

        Args:
            token: JWT access token to validate.

        Returns:
            Dict[str, Any]: Validation result with user data or error.
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256']
            )

            user_id = payload.get('user_id')
            if not user_id:
                return {
                    'success': False,
                    'error': 'Invalid token payload'
                }

            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'Token is valid'
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            return self.handle_service_error(e, 'token_validation')

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password with current password verification.

        Args:
            user_id: ID of the user changing password.
            current_password: Current plain text password.
            new_password: New plain text password.

        Returns:
            Dict[str, Any]: Password change result with success status or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Verify current password
            if not check_password_hash(user.password_hash, current_password):
                return {
                    'success': False,
                    'error': 'Current password is incorrect'
                }

            # Hash new password
            new_password_hash = generate_password_hash(new_password)

            # Update password
            self.update_record(user, password_hash=new_password_hash)

            self.logger.info(f"Password changed successfully for user: {user.email}")

            return {
                'success': True,
                'message': 'Password changed successfully'
            }

        except Exception as e:
            return self.handle_service_error(e, 'password_change')

    def send_email_verification(self, user_id: int) -> Dict[str, Any]:
        """
        Send email verification code to user.

        Args:
            user_id: ID of the user to send verification to.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            if user.email_verified:
                return {
                    'success': False,
                    'error': 'Email is already verified'
                }

            return self.email_service.send_email_verification(user)

        except Exception as e:
            return self.handle_service_error(e, 'send_email_verification')

    def verify_email(self, email: str, code: str) -> Dict[str, Any]:
        """
        Verify user's email with verification code.

        Args:
            email: User's email address.
            code: Verification code.

        Returns:
            Dict[str, Any]: Verification result with success status or error.
        """
        try:
            return self.email_service.verify_code(email, code, 'email_verification')

        except Exception as e:
            return self.handle_service_error(e, 'verify_email')

    def send_login_otp(self, email: str) -> Dict[str, Any]:
        """
        Send OTP for login to user's email.

        Args:
            email: User's email address.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            user = self._get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            return self.email_service.send_login_otp(user)

        except Exception as e:
            return self.handle_service_error(e, 'send_login_otp')

    def authenticate_with_otp(self, email: str, otp: str) -> Dict[str, Any]:
        """
        Authenticate user with OTP.

        Args:
            email: User's email address.
            otp: One-time password.

        Returns:
            Dict[str, Any]: Authentication result with success status, user data, and tokens or error.
        """
        try:
            # Verify OTP
            verification_result = self.email_service.verify_code(email, otp, 'login_otp')
            if not verification_result['success']:
                return verification_result

            user_data = verification_result['user']

            # Get the actual User object for token generation
            user = self._get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Generate tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)

            self.logger.info(f"User authenticated with OTP: {user.email}")

            return {
                'success': True,
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'Authentication successful'
            }

        except Exception as e:
            return self.handle_service_error(e, 'authenticate_with_otp')

    def send_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Send password reset link to user's email.

        Args:
            email: User's email address.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            user = self._get_user_by_email(email)
            if not user:
                # Don't reveal if user exists or not for security
                return {
                    'success': True,
                    'message': 'If the email exists, a password reset link has been sent'
                }

            return self.email_service.send_password_reset(user)

        except Exception as e:
            return self.handle_service_error(e, 'send_password_reset')

    def reset_password_with_code(self, code: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user's password using verification code.

        Args:
            code: Password reset verification code.
            new_password: New password.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Find the verification record
            verification = EmailVerification.query.filter_by(
                verification_code=code,
                verification_type='password_reset',
                is_used=False
            ).first()

            if not verification:
                return {
                    'success': False,
                    'error': 'Invalid or expired reset code'
                }

            if not verification.is_valid():
                return {
                    'success': False,
                    'error': 'Reset code has expired'
                }

            # Get user
            user = self.get_record_by_id(User, verification.user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Update password
            new_password_hash = generate_password_hash(new_password)
            self.update_record(user, password_hash=new_password_hash)

            # Mark verification as used
            verification.mark_as_used()

            self.logger.info(f"Password reset successful for user: {user.email}")

            return {
                'success': True,
                'message': 'Password reset successfully'
            }

        except Exception as e:
            return self.handle_service_error(e, 'reset_password_with_code')

    def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address.

        Returns:
            Optional[User]: User instance if found, None otherwise.
        """
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {str(e)}")
            return None

    def _generate_access_token(self, user: User) -> str:
        """
        Generate JWT access token for user.

        Args:
            user: User instance.

        Returns:
            str: JWT access token.
        """
        from flask_jwt_extended import create_access_token
        return create_access_token(identity=user.id)

    def _generate_refresh_token(self, user: User) -> str:
        """
        Generate JWT refresh token for user.

        Args:
            user: User instance.

        Returns:
            str: JWT refresh token.
        """
        from flask_jwt_extended import create_refresh_token
        return create_refresh_token(identity=user.id)
