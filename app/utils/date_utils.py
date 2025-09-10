"""
Date and time utilities for the Salah Reminders application.

This module provides date/time handling functions with proper timezone support
and prayer time calculations.
"""

from typing import Optional, Tuple
from datetime import datetime, date, time, timedelta
import pytz


def get_user_timezone(user_timezone: str) -> pytz.timezone:
    """
    Get timezone object for user's timezone.
    
    Args:
        user_timezone: User's timezone string.
        
    Returns:
        pytz.timezone: Timezone object.
    """
    try:
        return pytz.timezone(user_timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        # Default to UTC if timezone is invalid
        return pytz.UTC


def convert_to_user_timezone(dt: datetime, user_timezone: str) -> datetime:
    """
    Convert datetime to user's timezone.
    
    Args:
        dt: Datetime object to convert.
        user_timezone: User's timezone string.
        
    Returns:
        datetime: Datetime in user's timezone.
    """
    user_tz = get_user_timezone(user_timezone)
    
    if dt.tzinfo is None:
        # If datetime is naive, assume it's in UTC
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(user_tz)


def get_prayer_time_window(prayer_time: time, window_minutes: int = 30) -> Tuple[time, time]:
    """
    Get prayer time window (start and end times).
    
    Args:
        prayer_time: Prayer time.
        window_minutes: Window duration in minutes.
        
    Returns:
        Tuple[time, time]: (start_time, end_time) for the prayer window.
    """
    # Convert time to datetime for calculation
    prayer_datetime = datetime.combine(date.today(), prayer_time)
    
    # Calculate window start (prayer time)
    window_start = prayer_datetime.time()
    
    # Calculate window end (prayer time + window_minutes)
    window_end_datetime = prayer_datetime + timedelta(minutes=window_minutes)
    window_end = window_end_datetime.time()
    
    return window_start, window_end


def is_prayer_time_valid(prayer_time: time, user_timezone: str, 
                        window_minutes: int = 30) -> Tuple[bool, bool]:
    """
    Check if current time is within prayer time window.
    
    Args:
        prayer_time: Prayer time.
        user_timezone: User's timezone.
        window_minutes: Prayer time window in minutes.
        
    Returns:
        Tuple[bool, bool]: (can_complete, is_late) - whether prayer can be completed and if it's late.
    """
    user_tz = get_user_timezone(user_timezone)
    now = datetime.now(user_tz)
    
    # Get prayer time in user timezone
    prayer_datetime = user_tz.localize(
        datetime.combine(now.date(), prayer_time)
    )
    
    # Calculate prayer time window
    window_start = prayer_datetime
    window_end = prayer_datetime + timedelta(minutes=window_minutes)
    
    # Check if current time is within prayer window
    if now < window_start:
        return False, False  # Too early
    elif now <= window_end:
        return True, False   # On time
    else:
        return True, True    # Late but can still complete


def is_prayer_missed(prayer_time: time, user_timezone: str, 
                    window_minutes: int = 30) -> bool:
    """
    Check if a prayer is missed (time has passed without completion).
    
    Args:
        prayer_time: Prayer time.
        user_timezone: User's timezone.
        window_minutes: Prayer time window in minutes.
        
    Returns:
        bool: True if prayer is missed, False otherwise.
    """
    user_tz = get_user_timezone(user_timezone)
    now = datetime.now(user_tz)
    
    # Get prayer time in user timezone
    prayer_datetime = user_tz.localize(
        datetime.combine(now.date(), prayer_time)
    )
    
    # Calculate prayer time window end
    window_end = prayer_datetime + timedelta(minutes=window_minutes)
    
    # Check if prayer time has passed
    return now > window_end


def get_next_prayer_time(prayer_times: dict, user_timezone: str) -> Optional[Tuple[str, time]]:
    """
    Get the next upcoming prayer time.
    
    Args:
        prayer_times: Dictionary mapping prayer names to times.
        user_timezone: User's timezone.
        
    Returns:
        Optional[Tuple[str, time]]: (prayer_name, prayer_time) of next prayer or None.
    """
    user_tz = get_user_timezone(user_timezone)
    now = datetime.now(user_tz)
    current_time = now.time()
    
    # Find the next prayer time
    next_prayer = None
    min_time_diff = timedelta(days=1)  # Initialize with max possible difference
    
    for prayer_name, prayer_time in prayer_times.items():
        if prayer_time > current_time:
            time_diff = datetime.combine(date.today(), prayer_time) - datetime.combine(date.today(), current_time)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                next_prayer = (prayer_name, prayer_time)
    
    return next_prayer


def get_prayer_time_until_next(prayer_times: dict, user_timezone: str) -> Optional[timedelta]:
    """
    Get time remaining until next prayer.
    
    Args:
        prayer_times: Dictionary mapping prayer names to times.
        user_timezone: User's timezone.
        
    Returns:
        Optional[timedelta]: Time remaining until next prayer or None.
    """
    next_prayer = get_next_prayer_time(prayer_times, user_timezone)
    if not next_prayer:
        return None
    
    user_tz = get_user_timezone(user_timezone)
    now = datetime.now(user_tz)
    
    prayer_name, prayer_time = next_prayer
    prayer_datetime = user_tz.localize(
        datetime.combine(now.date(), prayer_time)
    )
    
    return prayer_datetime - now


def format_time_until_next(time_remaining: timedelta) -> str:
    """
    Format time remaining until next prayer in human-readable format.
    
    Args:
        time_remaining: Time remaining as timedelta.
        
    Returns:
        str: Formatted time string.
    """
    if not time_remaining:
        return "No upcoming prayers"
    
    total_seconds = int(time_remaining.total_seconds())
    
    if total_seconds < 0:
        return "Prayer time has passed"
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_date_range(start_date: date, end_date: date) -> list:
    """
    Get list of dates between start and end date (inclusive).
    
    Args:
        start_date: Start date.
        end_date: End date.
        
    Returns:
        list: List of date objects.
    """
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    
    return date_list


def get_month_dates(year: int, month: int) -> list:
    """
    Get all dates for a specific month.
    
    Args:
        year: Year.
        month: Month (1-12).
        
    Returns:
        list: List of date objects for the month.
    """
    # Get first day of month
    first_day = date(year, month, 1)
    
    # Get last day of month
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    return get_date_range(first_day, last_day)


def is_same_date(date1: date, date2: date) -> bool:
    """
    Check if two dates are the same.
    
    Args:
        date1: First date.
        date2: Second date.
        
    Returns:
        bool: True if dates are the same, False otherwise.
    """
    return date1 == date2


def is_today(date_obj: date) -> bool:
    """
    Check if a date is today.
    
    Args:
        date_obj: Date to check.
        
    Returns:
        bool: True if date is today, False otherwise.
    """
    return date_obj == date.today()


def is_yesterday(date_obj: date) -> bool:
    """
    Check if a date is yesterday.
    
    Args:
        date_obj: Date to check.
        
    Returns:
        bool: True if date is yesterday, False otherwise.
    """
    yesterday = date.today() - timedelta(days=1)
    return date_obj == yesterday


def is_tomorrow(date_obj: date) -> bool:
    """
    Check if a date is tomorrow.
    
    Args:
        date_obj: Date to check.
        
    Returns:
        bool: True if date is tomorrow, False otherwise.
    """
    tomorrow = date.today() + timedelta(days=1)
    return date_obj == tomorrow


def get_week_start_end(date_obj: date) -> Tuple[date, date]:
    """
    Get start and end dates of the week containing the given date.
    
    Args:
        date_obj: Date within the week.
        
    Returns:
        Tuple[date, date]: (week_start, week_end) dates.
    """
    # Get weekday (0 = Monday, 6 = Sunday)
    weekday = date_obj.weekday()
    
    # Calculate week start (Monday)
    week_start = date_obj - timedelta(days=weekday)
    
    # Calculate week end (Sunday)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_month_start_end(date_obj: date) -> Tuple[date, date]:
    """
    Get start and end dates of the month containing the given date.
    
    Args:
        date_obj: Date within the month.
        
    Returns:
        Tuple[date, date]: (month_start, month_end) dates.
    """
    # Month start is always the 1st
    month_start = date(date_obj.year, date_obj.month, 1)
    
    # Month end is the last day of the month
    if date_obj.month == 12:
        month_end = date(date_obj.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(date_obj.year, date_obj.month + 1, 1) - timedelta(days=1)
    
    return month_start, month_end


def parse_date_string(date_string: str, format: str = '%Y-%m-%d') -> Optional[date]:
    """
    Parse date string to date object.
    
    Args:
        date_string: Date string to parse.
        format: Date format string.
        
    Returns:
        Optional[date]: Parsed date object or None if parsing fails.
    """
    try:
        return datetime.strptime(date_string, format).date()
    except ValueError:
        return None


def parse_time_string(time_string: str, format: str = '%H:%M') -> Optional[time]:
    """
    Parse time string to time object.
    
    Args:
        time_string: Time string to parse.
        format: Time format string.
        
    Returns:
        Optional[time]: Parsed time object or None if parsing fails.
    """
    try:
        return datetime.strptime(time_string, format).time()
    except ValueError:
        return None
