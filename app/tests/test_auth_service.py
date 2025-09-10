"""
Unit tests for the authentication service.

This module contains comprehensive unit tests for the AuthService class,
testing user registration, authentication, token management, and password handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import check_password_hash

from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.exceptions import ValidationError, AuthenticationError, UserNotFoundError


class TestAuthService:
    """Test class for AuthService."""
    
    def test_init(self, app):
        """Test AuthService initialization."""
        with app.app_context():
            service = AuthService()
            assert service is not None
            assert service.jwt_config is not None
    
    def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration."""
        with patch('app.services.auth_service.AuthService._get_user_by_email', return_value=None):
            service = AuthService()
            result = service.register_user(sample_user_data)
            
            assert result['success'] is True
            assert 'user' in result
            assert result['user']['email'] == sample_user_data['email']
            assert result['user']['first_name'] == sample_user_data['first_name']
            assert result['user']['last_name'] == sample_user_data['last_name']
    
    def test_register_user_missing_fields(self, db_session):
        """Test user registration with missing required fields."""
        service = AuthService()
        incomplete_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
            # Missing first_name, last_name, username
        }
        
        result = service.register_user(incomplete_data)
        
        assert result['success'] is False
        assert 'Missing required field' in result['error']
    
    def test_register_user_email_already_exists(self, db_session, sample_user_data, sample_user):
        """Test user registration with existing email."""
        with patch('app.services.auth_service.AuthService._get_user_by_email', return_value=sample_user):
            service = AuthService()
            result = service.register_user(sample_user_data)
            
            assert result['success'] is False
            assert 'already exists' in result['error']
    
    def test_authenticate_user_success(self, db_session, sample_user):
        """Test successful user authentication."""
        with patch('app.services.auth_service.AuthService._get_user_by_email', return_value=sample_user):
            with patch('werkzeug.security.check_password_hash', return_value=True):
                service = AuthService()
                result = service.authenticate_user('test@example.com', 'password')
                
                assert result['success'] is True
                assert 'access_token' in result
                assert 'refresh_token' in result
                assert 'user' in result
    
    def test_authenticate_user_invalid_email(self, db_session):
        """Test authentication with non-existent email."""
        with patch('app.services.auth_service.AuthService._get_user_by_email', return_value=None):
            service = AuthService()
            result = service.authenticate_user('nonexistent@example.com', 'password')
            
            assert result['success'] is False
            assert 'Invalid email or password' in result['error']
    
    def test_authenticate_user_invalid_password(self, db_session, sample_user):
        """Test authentication with invalid password."""
        with patch('app.services.auth_service.AuthService._get_user_by_email', return_value=sample_user):
            with patch('werkzeug.security.check_password_hash', return_value=False):
                service = AuthService()
                result = service.authenticate_user('test@example.com', 'wrongpassword')
                
                assert result['success'] is False
                assert 'Invalid email or password' in result['error']
    
    def test_validate_token_success(self, db_session, sample_user):
        """Test successful token validation."""
        with patch('app.services.auth_service.AuthService.get_record_by_id', return_value=sample_user):
            with patch('jwt.decode') as mock_decode:
                mock_decode.return_value = {'user_id': sample_user.id}
                
                service = AuthService()
                result = service.validate_token('valid_token')
                
                assert result['success'] is True
                assert 'user' in result
    
    def test_validate_token_expired(self, db_session):
        """Test token validation with expired token."""
        with patch('jwt.decode') as mock_decode:
            from jwt import ExpiredSignatureError
            mock_decode.side_effect = ExpiredSignatureError('Token expired')
            
            service = AuthService()
            result = service.validate_token('expired_token')
            
            assert result['success'] is False
            assert 'Token expired' in result['error']
    
    def test_validate_token_invalid(self, db_session):
        """Test token validation with invalid token."""
        with patch('jwt.decode') as mock_decode:
            from jwt import InvalidTokenError
            mock_decode.side_effect = InvalidTokenError('Invalid token')
            
            service = AuthService()
            result = service.validate_token('invalid_token')
            
            assert result['success'] is False
            assert 'Invalid token' in result['error']
    
    def test_refresh_access_token_success(self, db_session, sample_user):
        """Test successful access token refresh."""
        with patch('app.services.auth_service.AuthService.get_record_by_id', return_value=sample_user):
            with patch('jwt.decode') as mock_decode:
                mock_decode.return_value = {'user_id': sample_user.id}
                
                service = AuthService()
                result = service.refresh_access_token('valid_refresh_token')
                
                assert result['success'] is True
                assert 'access_token' in result
    
    def test_refresh_access_token_expired(self, db_session):
        """Test access token refresh with expired refresh token."""
        with patch('jwt.decode') as mock_decode:
            from jwt import ExpiredSignatureError
            mock_decode.side_effect = ExpiredSignatureError('Token expired')
            
            service = AuthService()
            result = service.refresh_access_token('expired_refresh_token')
            
            assert result['success'] is False
            assert 'Refresh token expired' in result['error']
    
    def test_change_password_success(self, db_session, sample_user):
        """Test successful password change."""
        with patch('app.services.auth_service.AuthService.get_record_by_id', return_value=sample_user):
            with patch('werkzeug.security.check_password_hash', return_value=True):
                service = AuthService()
                result = service.change_password(sample_user.id, 'oldpassword', 'newpassword')
                
                assert result['success'] is True
                assert 'Password changed successfully' in result['message']
    
    def test_change_password_user_not_found(self, db_session):
        """Test password change with non-existent user."""
        with patch('app.services.auth_service.AuthService.get_record_by_id', return_value=None):
            service = AuthService()
            result = service.change_password(999, 'oldpassword', 'newpassword')
            
            assert result['success'] is False
            assert 'User not found' in result['error']
    
    def test_change_password_incorrect_current(self, db_session, sample_user):
        """Test password change with incorrect current password."""
        with patch('app.services.auth_service.AuthService.get_record_by_id', return_value=sample_user):
            with patch('werkzeug.security.check_password_hash', return_value=False):
                service = AuthService()
                result = service.change_password(sample_user.id, 'wrongpassword', 'newpassword')
                
                assert result['success'] is False
                assert 'Current password is incorrect' in result['error']
    
    def test_generate_access_token(self, db_session, sample_user):
        """Test access token generation."""
        service = AuthService()
        token = service._generate_access_token(sample_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_refresh_token(self, db_session, sample_user):
        """Test refresh token generation."""
        service = AuthService()
        token = service._generate_refresh_token(sample_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_get_user_by_email_success(self, db_session, sample_user):
        """Test getting user by email."""
        service = AuthService()
        user = service._get_user_by_email(sample_user.email)
        
        assert user is not None
        assert user.email == sample_user.email
    
    def test_get_user_by_email_not_found(self, db_session):
        """Test getting non-existent user by email."""
        service = AuthService()
        user = service._get_user_by_email('nonexistent@example.com')
        
        assert user is None
    
    def test_handle_service_error(self, db_session):
        """Test service error handling."""
        service = AuthService()
        error = Exception('Test error')
        result = service.handle_service_error(error, 'test_operation')
        
        assert result['success'] is False
        assert 'Test error' in result['error']
        assert result['operation'] == 'test_operation'
        assert 'timestamp' in result
