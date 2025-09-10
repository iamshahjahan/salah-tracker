"""
Formatting utilities for the Salah Reminders application.

This module provides formatting functions for dates, times, and other data
with proper localization and user-friendly display.
"""

from typing import Any, Dict, Optional
from datetime import datetime, date, time
import pytz


def format_prayer_time(prayer_time: time, timezone: Optional[str] = None) -> str:
    """
    Format prayer time for display.
    
    Args:
        prayer_time: Time object to format.
        timezone: Optional timezone for display.
        
    Returns:
        str: Formatted time string.
    """
    if not isinstance(prayer_time, time):
        return "Invalid time"
    
    return prayer_time.strftime('%H:%M')


def format_date(date_obj: date, format_type: str = 'display') -> str:
    """
    Format date for display.
    
    Args:
        date_obj: Date object to format.
        format_type: Type of formatting ('display', 'api', 'short').
        
    Returns:
        str: Formatted date string.
    """
    if not isinstance(date_obj, date):
        return "Invalid date"
    
    format_map = {
        'display': '%B %d, %Y',  # January 15, 2024
        'api': '%Y-%m-%d',       # 2024-01-15
        'short': '%m/%d/%Y',     # 01/15/2024
        'iso': '%Y-%m-%d'        # 2024-01-15
    }
    
    format_str = format_map.get(format_type, format_map['display'])
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj: datetime, format_type: str = 'display', 
                   timezone: Optional[str] = None) -> str:
    """
    Format datetime for display.
    
    Args:
        datetime_obj: Datetime object to format.
        format_type: Type of formatting ('display', 'api', 'short').
        timezone: Optional timezone for display.
        
    Returns:
        str: Formatted datetime string.
    """
    if not isinstance(datetime_obj, datetime):
        return "Invalid datetime"
    
    # Convert to timezone if specified
    if timezone:
        try:
            tz = pytz.timezone(timezone)
            if datetime_obj.tzinfo is None:
                datetime_obj = tz.localize(datetime_obj)
            else:
                datetime_obj = datetime_obj.astimezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            pass  # Use original datetime if timezone is invalid
    
    format_map = {
        'display': '%B %d, %Y at %I:%M %p',  # January 15, 2024 at 02:30 PM
        'api': '%Y-%m-%dT%H:%M:%S',          # 2024-01-15T14:30:00
        'short': '%m/%d/%Y %I:%M %p',        # 01/15/2024 02:30 PM
        'iso': '%Y-%m-%dT%H:%M:%S%z'         # 2024-01-15T14:30:00+00:00
    }
    
    format_str = format_map.get(format_type, format_map['display'])
    return datetime_obj.strftime(format_str)


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds.
        
    Returns:
        str: Formatted duration string.
    """
    if not isinstance(seconds, int) or seconds < 0:
        return "Invalid duration"
    
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if hours == 0:
            return f"{days} day{'s' if days != 1 else ''}"
        else:
            return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage value for display.
    
    Args:
        value: Percentage value (0-100).
        decimals: Number of decimal places.
        
    Returns:
        str: Formatted percentage string.
    """
    if not isinstance(value, (int, float)):
        return "Invalid percentage"
    
    # Clamp value between 0 and 100
    value = max(0, min(100, value))
    
    return f"{value:.{decimals}f}%"


def format_file_size(bytes_size: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        bytes_size: File size in bytes.
        
    Returns:
        str: Formatted file size string.
    """
    if not isinstance(bytes_size, int) or bytes_size < 0:
        return "Invalid size"
    
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(size_units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {size_units[unit_index]}"


def format_phone_number(phone_number: str) -> str:
    """
    Format phone number for display.
    
    Args:
        phone_number: Raw phone number string.
        
    Returns:
        str: Formatted phone number.
    """
    if not phone_number:
        return ""
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone_number))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone_number  # Return original if can't format


def format_user_name(first_name: str, last_name: str) -> str:
    """
    Format user's full name for display.
    
    Args:
        first_name: User's first name.
        last_name: User's last name.
        
    Returns:
        str: Formatted full name.
    """
    first_name = first_name.strip() if first_name else ""
    last_name = last_name.strip() if last_name else ""
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return "Unknown User"


def format_prayer_status(completed: bool, is_late: bool = False, is_qada: bool = False) -> str:
    """
    Format prayer completion status for display.
    
    Args:
        completed: Whether prayer is completed.
        is_late: Whether prayer was completed late.
        is_qada: Whether prayer is marked as Qada.
        
    Returns:
        str: Formatted status string.
    """
    if not completed:
        return "Not Completed"
    elif is_qada:
        return "Qada"
    elif is_late:
        return "Completed (Late)"
    else:
        return "Completed"


def format_api_response(data: Any, success: bool = True, message: str = "", 
                       errors: Optional[list] = None) -> Dict[str, Any]:
    """
    Format API response in consistent structure.
    
    Args:
        data: Response data.
        success: Whether the operation was successful.
        message: Response message.
        errors: List of error messages.
        
    Returns:
        Dict[str, Any]: Formatted API response.
    """
    response = {
        'success': success,
        'data': data,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if errors:
        response['errors'] = errors
    
    return response


def format_validation_errors(errors: list) -> str:
    """
    Format validation errors for display.
    
    Args:
        errors: List of validation error messages.
        
    Returns:
        str: Formatted error message.
    """
    if not errors:
        return ""
    
    if len(errors) == 1:
        return errors[0]
    else:
        return f"Multiple errors: {'; '.join(errors)}"


def format_location(latitude: float, longitude: float, city: str = "", 
                   country: str = "") -> str:
    """
    Format location information for display.
    
    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        city: City name.
        country: Country name.
        
    Returns:
        str: Formatted location string.
    """
    if city and country:
        return f"{city}, {country}"
    elif city:
        return city
    elif country:
        return country
    else:
        return f"{latitude:.4f}, {longitude:.4f}"
