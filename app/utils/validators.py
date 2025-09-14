"""
Validation utilities for the Salah Tracker application.

This module provides validation functions for user inputs, data formats,
and business logic validation with proper error handling.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.

    Args:
        email: Email address to validate.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if email is None:
        return False, "Email is required"
    
    if not email:
        return False, "Email is required"

    if not isinstance(email, str):
        return False, "Email must be a string"

    # Basic email regex pattern (more strict)
    email_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
    
    # Additional check for consecutive dots
    if '..' in email:
        return False, "Invalid email format"

    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address is too long"

    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength and format.

    Args:
        password: Password to validate.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if not isinstance(password, str):
        return False, "Password must be a string"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password is too long"

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(latitude, (int, float)):
        return False, "Latitude must be a number"

    if not isinstance(longitude, (int, float)):
        return False, "Longitude must be a number"

    if not (-90 <= latitude <= 90):
        return False, "Latitude must be between -90 and 90 degrees"

    if not (-180 <= longitude <= 180):
        return False, "Longitude must be between -180 and 180 degrees"

    return True, None


def validate_phone_number(phone_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.

    Args:
        phone_number: Phone number to validate.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not phone_number:
        return True, None  # Phone number is optional

    if not isinstance(phone_number, str):
        return False, "Phone number must be a string"

    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone_number)

    if len(digits_only) < 10:
        return False, "Phone number must have at least 10 digits"

    if len(digits_only) > 15:
        return False, "Phone number is too long"

    return True, None


def validate_date_string(date_string: str, format: str = '%Y-%m-%d') -> Tuple[bool, Optional[str]]:
    """
    Validate date string format.

    Args:
        date_string: Date string to validate.
        format: Expected date format.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not date_string:
        return False, "Date is required"

    if not isinstance(date_string, str):
        return False, "Date must be a string"

    try:
        datetime.strptime(date_string, format)
        return True, None
    except ValueError:
        return False, f"Invalid date format. Expected {format}"


def validate_time_string(time_string: str, format: str = '%H:%M') -> Tuple[bool, Optional[str]]:
    """
    Validate time string format.

    Args:
        time_string: Time string to validate.
        format: Expected time format.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not time_string:
        return False, "Time is required"

    if not isinstance(time_string, str):
        return False, "Time must be a string"

    try:
        datetime.strptime(time_string, format)
        return True, None
    except ValueError:
        return False, f"Invalid time format. Expected {format}"


def validate_user_registration_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate user registration data.

    Args:
        data: Dictionary containing user registration data.

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")

    # Validate email
    if data.get('email'):
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            errors.append(error)

    # Validate password
    if data.get('password'):
        is_valid, error = validate_password(data['password'])
        if not is_valid:
            errors.append(error)

    # Validate phone number (optional)
    if data.get('phone_number'):
        is_valid, error = validate_phone_number(data['phone_number'])
        if not is_valid:
            errors.append(error)

    # Validate coordinates (optional)
    if data.get('location_lat') is not None and data.get('location_lng') is not None:
        is_valid, error = validate_coordinates(data['location_lat'], data['location_lng'])
        if not is_valid:
            errors.append(error)

    # Validate name fields
    if data.get('first_name') and len(data['first_name'].strip()) < 2:
        errors.append("First name must be at least 2 characters long")

    if data.get('last_name') and len(data['last_name'].strip()) < 2:
        errors.append("Last name must be at least 2 characters long")

    return len(errors) == 0, errors


def validate_prayer_completion_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate prayer completion data.

    Args:
        data: Dictionary containing prayer completion data.

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []

    # Validate required fields
    if not data.get('prayer_id'):
        errors.append("prayer_id is required")

    # Validate prayer_id is integer
    if data.get('prayer_id'):
        try:
            int(data['prayer_id'])
        except (ValueError, TypeError):
            errors.append("Prayer ID must be a valid integer")

    return len(errors) == 0, errors


def validate_pagination_params(page: int, per_page: int) -> Tuple[bool, Optional[str]]:
    """
    Validate pagination parameters.

    Args:
        page: Page number (1-based).
        per_page: Number of items per page.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(page, int) or page < 1:
        return False, "Page must be a positive integer"

    if not isinstance(per_page, int) or per_page < 1:
        return False, "Per page must be a positive integer"

    if per_page > 100:
        return False, "Per page cannot exceed 100 items"

    return True, None


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input by removing dangerous characters and limiting length.

    Args:
        value: String to sanitize.
        max_length: Maximum allowed length.

    Returns:
        str: Sanitized string.
    """
    if value is None:
        return ""
    
    if not isinstance(value, str):
        return ""

    # Remove potentially dangerous characters (only < and >)
    sanitized = re.sub(r'[<>]', '', value)

    # Strip whitespace
    sanitized = sanitized.strip()

    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_timezone(timezone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate timezone string.

    Args:
        timezone: Timezone string to validate.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not timezone:
        return False, "Timezone is required"

    if not isinstance(timezone, str):
        return False, "Timezone must be a string"

    # Common timezone patterns
    timezone_pattern = r'^[A-Za-z_/]+$'

    if not re.match(timezone_pattern, timezone):
        return False, "Invalid timezone format"

    # Check if it's a valid timezone (basic check)
    try:
        import pytz
        pytz.timezone(timezone)
        return True, None
    except pytz.exceptions.UnknownTimeZoneError:
        return False, "Unknown timezone"
    except ImportError:
        # If pytz is not available, just do basic format validation
        return True, None
