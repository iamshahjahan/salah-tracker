"""
Unit tests for validation utilities.

This module contains comprehensive unit tests for all validation functions,
testing input validation, format validation, and business logic validation.
"""

import pytest
from datetime import date, time

from app.utils.validators import (
    validate_email, validate_password, validate_coordinates,
    validate_phone_number, validate_date_string, validate_time_string,
    validate_user_registration_data, validate_prayer_completion_data,
    validate_pagination_params, sanitize_string, validate_timezone
)


class TestEmailValidation:
    """Test class for email validation."""
    
    def test_valid_email(self):
        """Test valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is True
            assert error is None
    
    def test_invalid_email(self):
        """Test invalid email addresses."""
        invalid_emails = [
            '',
            None,
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            'user..name@example.com',
            'user@example..com',
            'a' * 300 + '@example.com'  # Too long
        ]
        
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is False
            assert error is not None
    
    def test_email_type_validation(self):
        """Test email type validation."""
        is_valid, error = validate_email(123)
        assert is_valid is False
        assert 'must be a string' in error


class TestPasswordValidation:
    """Test class for password validation."""
    
    def test_valid_password(self):
        """Test valid passwords."""
        valid_passwords = [
            'Password123!',
            'MySecurePass1@',
            'Test123#Pass',
            'ValidPass9$'
        ]
        
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid is True
            assert error is None
    
    def test_invalid_password(self):
        """Test invalid passwords."""
        invalid_passwords = [
            '',  # Empty
            'short',  # Too short
            'nouppercase123!',  # No uppercase
            'NOLOWERCASE123!',  # No lowercase
            'NoNumbers!',  # No numbers
            'NoSpecialChars123',  # No special characters
            'a' * 200  # Too long
        ]
        
        for password in invalid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid is False
            assert error is not None
    
    def test_password_type_validation(self):
        """Test password type validation."""
        is_valid, error = validate_password(123)
        assert is_valid is False
        assert 'must be a string' in error


class TestCoordinateValidation:
    """Test class for coordinate validation."""
    
    def test_valid_coordinates(self):
        """Test valid coordinates."""
        valid_coords = [
            (0, 0),
            (90, 180),
            (-90, -180),
            (12.9716, 77.5946),
            (0.0, 0.0)
        ]
        
        for lat, lng in valid_coords:
            is_valid, error = validate_coordinates(lat, lng)
            assert is_valid is True
            assert error is None
    
    def test_invalid_coordinates(self):
        """Test invalid coordinates."""
        invalid_coords = [
            (91, 0),  # Latitude too high
            (-91, 0),  # Latitude too low
            (0, 181),  # Longitude too high
            (0, -181),  # Longitude too low
            ('invalid', 0),  # Invalid type
            (0, 'invalid'),  # Invalid type
        ]
        
        for lat, lng in invalid_coords:
            is_valid, error = validate_coordinates(lat, lng)
            assert is_valid is False
            assert error is not None


class TestPhoneNumberValidation:
    """Test class for phone number validation."""
    
    def test_valid_phone_numbers(self):
        """Test valid phone numbers."""
        valid_phones = [
            '1234567890',
            '+1-234-567-8900',
            '(123) 456-7890',
            '+91 98765 43210',
            '123-456-7890',
            None,  # Optional field
            ''  # Empty string
        ]
        
        for phone in valid_phones:
            is_valid, error = validate_phone_number(phone)
            assert is_valid is True
            assert error is None
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers."""
        invalid_phones = [
            '123',  # Too short
            '12345678901234567890',  # Too long
            1234567890,  # Not a string
        ]
        
        for phone in invalid_phones:
            is_valid, error = validate_phone_number(phone)
            assert is_valid is False
            assert error is not None


class TestDateStringValidation:
    """Test class for date string validation."""
    
    def test_valid_date_strings(self):
        """Test valid date strings."""
        valid_dates = [
            '2024-01-15',
            '2023-12-31',
            '2024-02-29'  # Leap year
        ]
        
        for date_str in valid_dates:
            is_valid, error = validate_date_string(date_str)
            assert is_valid is True
            assert error is None
    
    def test_invalid_date_strings(self):
        """Test invalid date strings."""
        invalid_dates = [
            '',
            None,
            'invalid-date',
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            '2024/01/15',  # Wrong format
            20240115  # Not a string
        ]
        
        for date_str in invalid_dates:
            is_valid, error = validate_date_string(date_str)
            assert is_valid is False
            assert error is not None


class TestTimeStringValidation:
    """Test class for time string validation."""
    
    def test_valid_time_strings(self):
        """Test valid time strings."""
        valid_times = [
            '12:00',
            '00:00',
            '23:59',
            '05:30'
        ]
        
        for time_str in valid_times:
            is_valid, error = validate_time_string(time_str)
            assert is_valid is True
            assert error is None
    
    def test_invalid_time_strings(self):
        """Test invalid time strings."""
        invalid_times = [
            '',
            None,
            'invalid-time',
            '25:00',  # Invalid hour
            '12:60',  # Invalid minute
            '12.00',  # Wrong format
            1200  # Not a string
        ]
        
        for time_str in invalid_times:
            is_valid, error = validate_time_string(time_str)
            assert is_valid is False
            assert error is not None


class TestUserRegistrationValidation:
    """Test class for user registration data validation."""
    
    def test_valid_registration_data(self):
        """Test valid user registration data."""
        valid_data = {
            'username': 'testuser@example.com',
            'email': 'testuser@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'location_lat': 12.9716,
            'location_lng': 77.5946
        }
        
        is_valid, errors = validate_user_registration_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_required_fields(self):
        """Test registration data with missing required fields."""
        incomplete_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
            # Missing username, first_name, last_name
        }
        
        is_valid, errors = validate_user_registration_data(incomplete_data)
        assert is_valid is False
        assert len(errors) > 0
        assert any('required' in error for error in errors)
    
    def test_invalid_email_in_registration(self):
        """Test registration data with invalid email."""
        invalid_data = {
            'username': 'testuser@example.com',
            'email': 'invalid-email',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        is_valid, errors = validate_user_registration_data(invalid_data)
        assert is_valid is False
        assert any('email' in error.lower() for error in errors)
    
    def test_invalid_password_in_registration(self):
        """Test registration data with invalid password."""
        invalid_data = {
            'username': 'testuser@example.com',
            'email': 'test@example.com',
            'password': 'weak',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        is_valid, errors = validate_user_registration_data(invalid_data)
        assert is_valid is False
        assert any('password' in error.lower() for error in errors)
    
    def test_invalid_coordinates_in_registration(self):
        """Test registration data with invalid coordinates."""
        invalid_data = {
            'username': 'testuser@example.com',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'location_lat': 200,  # Invalid latitude
            'location_lng': 77.5946
        }
        
        is_valid, errors = validate_user_registration_data(invalid_data)
        assert is_valid is False
        assert any('latitude' in error.lower() for error in errors)
    
    def test_short_names_in_registration(self):
        """Test registration data with short names."""
        invalid_data = {
            'username': 'testuser@example.com',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'A',  # Too short
            'last_name': 'B'    # Too short
        }
        
        is_valid, errors = validate_user_registration_data(invalid_data)
        assert is_valid is False
        assert any('characters long' in error for error in errors)


class TestPrayerCompletionValidation:
    """Test class for prayer completion data validation."""
    
    def test_valid_prayer_completion_data(self):
        """Test valid prayer completion data."""
        valid_data = {
            'prayer_id': 123
        }
        
        is_valid, errors = validate_prayer_completion_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_prayer_id(self):
        """Test prayer completion data with missing prayer ID."""
        invalid_data = {}
        
        is_valid, errors = validate_prayer_completion_data(invalid_data)
        assert is_valid is False
        assert any('prayer_id' in error.lower() for error in errors)
    
    def test_invalid_prayer_id_type(self):
        """Test prayer completion data with invalid prayer ID type."""
        invalid_data = {
            'prayer_id': 'invalid'
        }
        
        is_valid, errors = validate_prayer_completion_data(invalid_data)
        assert is_valid is False
        assert any('integer' in error.lower() for error in errors)


class TestPaginationValidation:
    """Test class for pagination parameters validation."""
    
    def test_valid_pagination_params(self):
        """Test valid pagination parameters."""
        is_valid, error = validate_pagination_params(1, 10)
        assert is_valid is True
        assert error is None
    
    def test_invalid_page_number(self):
        """Test invalid page number."""
        is_valid, error = validate_pagination_params(0, 10)
        assert is_valid is False
        assert 'positive integer' in error
    
    def test_invalid_per_page(self):
        """Test invalid per page value."""
        is_valid, error = validate_pagination_params(1, 0)
        assert is_valid is False
        assert 'positive integer' in error
    
    def test_per_page_too_large(self):
        """Test per page value too large."""
        is_valid, error = validate_pagination_params(1, 200)
        assert is_valid is False
        assert 'exceed 100' in error


class TestStringSanitization:
    """Test class for string sanitization."""
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        test_cases = [
            ('<script>alert("xss")</script>', 'scriptalert("xss")/script'),
            ('  whitespace  ', 'whitespace'),
            ('normal text', 'normal text'),
            ('', ''),
            (None, '')
        ]
        
        for input_str, expected in test_cases:
            result = sanitize_string(input_str)
            assert result == expected
    
    def test_sanitize_string_with_max_length(self):
        """Test string sanitization with max length."""
        long_string = 'a' * 100
        result = sanitize_string(long_string, max_length=50)
        assert len(result) == 50
        assert result == 'a' * 50


class TestTimezoneValidation:
    """Test class for timezone validation."""
    
    def test_valid_timezones(self):
        """Test valid timezone strings."""
        valid_timezones = [
            'UTC',
            'Asia/Kolkata',
            'America/New_York',
            'Europe/London',
            'Australia/Sydney'
        ]
        
        for timezone in valid_timezones:
            is_valid, error = validate_timezone(timezone)
            assert is_valid is True
            assert error is None
    
    def test_invalid_timezones(self):
        """Test invalid timezone strings."""
        invalid_timezones = [
            '',
            None,
            'invalid-timezone',
            'Asia/Invalid',
            '123',
            'timezone with spaces'
        ]
        
        for timezone in invalid_timezones:
            is_valid, error = validate_timezone(timezone)
            assert is_valid is False
            assert error is not None
    
    def test_timezone_type_validation(self):
        """Test timezone type validation."""
        is_valid, error = validate_timezone(123)
        assert is_valid is False
        assert 'must be a string' in error
