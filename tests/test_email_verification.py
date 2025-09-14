"""
Unit tests for email verification functionality.

This module contains tests for the EmailVerification model and email service
functionality including verification code generation, validation, and email sending.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.models.email_verification import EmailVerification
from app.models.user import User
from app.services.email_service import EmailService


class TestEmailVerification:
    """Test class for EmailVerification model."""

    def test_generate_verification_code(self):
        """Test verification code generation."""
        code = EmailVerification.generate_verification_code()
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_verification_code_custom_length(self):
        """Test verification code generation with custom length."""
        code = EmailVerification.generate_verification_code(8)
        assert isinstance(code, str)
        assert len(code) == 8
        assert code.isdigit()

    def test_create_verification(self, db_session, sample_user):
        """Test creating a verification record."""
        verification = EmailVerification.create_verification(
            user_id=sample_user.id,
            email=sample_user.email,
            verification_type='email_verification',
            expires_in_minutes=15
        )

        assert verification is not None
        assert verification.user_id == sample_user.id
        assert verification.email == sample_user.email
        assert verification.verification_type == 'email_verification'
        assert verification.is_used is False
        assert verification.expires_at > datetime.utcnow()

    def test_is_valid_fresh_verification(self, db_session, sample_user):
        """Test validation of fresh verification code."""
        verification = EmailVerification.create_verification(
            user_id=sample_user.id,
            email=sample_user.email,
            verification_type='email_verification'
        )

        assert verification.is_valid() is True

    def test_is_valid_expired_verification(self, db_session, sample_user):
        """Test validation of expired verification code."""
        verification = EmailVerification.create_verification(
            user_id=sample_user.id,
            email=sample_user.email,
            verification_type='email_verification',
            expires_in_minutes=-1  # Already expired
        )

        assert verification.is_valid() is False

    def test_is_valid_used_verification(self, db_session, sample_user):
        """Test validation of used verification code."""
        verification = EmailVerification.create_verification(
            user_id=sample_user.id,
            email=sample_user.email,
            verification_type='email_verification'
        )

        verification.mark_as_used()
        assert verification.is_valid() is False

    def test_mark_as_used(self, db_session, sample_user):
        """Test marking verification as used."""
        verification = EmailVerification.create_verification(
            user_id=sample_user.id,
            email=sample_user.email,
            verification_type='email_verification'
        )

        assert verification.is_used is False
        verification.mark_as_used()
        assert verification.is_used is True


class TestEmailService:
    """Test class for EmailService."""

    def test_init(self, app):
        """Test EmailService initialization."""
        with app.app_context():
            service = EmailService()
            assert service is not None
            assert service.email_service is not None

    @patch('app.services.email_service.EmailService._send_email')
    def test_send_email_verification_success(self, mock_send_email, app, sample_user):
        """Test successful email verification sending."""
        mock_send_email.return_value = True

        with app.app_context():
            service = EmailService()
            result = service.send_email_verification(sample_user)

            assert result['success'] is True
            assert 'verification_id' in result
            mock_send_email.assert_called_once()

    @patch('app.services.email_service.EmailService._send_email')
    def test_send_email_verification_failure(self, mock_send_email, app, sample_user):
        """Test email verification sending failure."""
        mock_send_email.return_value = False

        with app.app_context():
            service = EmailService()
            result = service.send_email_verification(sample_user)

            assert result['success'] is False
            assert 'Failed to send verification email' in result['error']

    @patch('app.services.email_service.EmailService._send_email')
    def test_send_login_otp_success(self, mock_send_email, app, sample_user):
        """Test successful login OTP sending."""
        mock_send_email.return_value = True

        with app.app_context():
            service = EmailService()
            result = service.send_login_otp(sample_user)

            assert result['success'] is True
            assert 'verification_id' in result
            mock_send_email.assert_called_once()

    @patch('app.services.email_service.EmailService._send_email')
    def test_send_password_reset_success(self, mock_send_email, app, sample_user):
        """Test successful password reset email sending."""
        mock_send_email.return_value = True

        with app.app_context():
            service = EmailService()
            result = service.send_password_reset(sample_user)

            assert result['success'] is True
            mock_send_email.assert_called_once()

    def test_verify_code_success(self, app, sample_user):
        """Test successful code verification."""
        with app.app_context():
            # Create a verification record
            verification = EmailVerification.create_verification(
                user_id=sample_user.id,
                email=sample_user.email,
                verification_type='email_verification'
            )

            service = EmailService()
            result = service.verify_code(
                sample_user.email,
                verification.verification_code,
                'email_verification'
            )

            assert result['success'] is True
            assert result['user']['id'] == sample_user.id

    def test_verify_code_invalid(self, app, sample_user):
        """Test verification with invalid code."""
        with app.app_context():
            service = EmailService()
            result = service.verify_code(
                sample_user.email,
                'invalid_code',
                'email_verification'
            )

            assert result['success'] is False
            assert 'Invalid verification code' in result['error']

    def test_verify_code_expired(self, app, sample_user):
        """Test verification with expired code."""
        with app.app_context():
            # Create an expired verification record
            verification = EmailVerification.create_verification(
                user_id=sample_user.id,
                email=sample_user.email,
                verification_type='email_verification',
                expires_in_minutes=-1  # Already expired
            )

            service = EmailService()
            result = service.verify_code(
                sample_user.email,
                verification.verification_code,
                'email_verification'
            )

            assert result['success'] is False
            assert 'Verification code has expired' in result['error']
