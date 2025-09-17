"""Timezone utility functions for consistent datetime handling across the application.

This module provides utility functions for handling timezone conversions,
UTC storage, and localized datetime operations throughout the application.
"""

from datetime import datetime
from typing import Optional

import pytz
from zoneinfo import ZoneInfo


def get_utc_now() -> datetime:
    """Get current datetime in UTC timezone.

    Returns:
        datetime: Current datetime in UTC timezone.
    """
    return datetime.now(pytz.UTC)


def to_utc(dt: datetime, source_timezone: Optional[str] = None) -> datetime:
    """Convert a datetime to UTC.

    Args:
        dt: The datetime to convert.
        source_timezone: The source timezone (IANA identifier). If None, assumes UTC.

    Returns:
        datetime: The datetime converted to UTC.
    """
    if dt.tzinfo is None:
        # If naive datetime, assume it's in the source timezone
        if source_timezone:
            dt = dt.replace(tzinfo=ZoneInfo(source_timezone))
        else:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))

    return dt.astimezone(ZoneInfo('UTC'))


def to_local(dt: datetime, target_timezone: str) -> datetime:
    """Convert a UTC datetime to a local timezone.

    Args:
        dt: The UTC datetime to convert.
        target_timezone: The target timezone (IANA identifier).

    Returns:
        datetime: The datetime converted to the target timezone.
    """
    if dt.tzinfo is None:
        # If naive datetime, assume it's UTC
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))

    return dt.astimezone(ZoneInfo(target_timezone))


def format_datetime_utc(dt: Optional[datetime]) -> Optional[str]:
    """Format a datetime as ISO string in UTC.

    Args:
        dt: The datetime to format.

    Returns:
        str: ISO formatted datetime string in UTC, or None if dt is None.
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))

    return dt.astimezone(ZoneInfo('UTC')).isoformat()


def format_datetime_local(dt: Optional[datetime], timezone: str) -> Optional[str]:
    """Format a datetime as ISO string in the specified timezone.

    Args:
        dt: The datetime to format.
        timezone: The target timezone (IANA identifier).

    Returns:
        str: ISO formatted datetime string in the target timezone, or None if dt is None.
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))

    return dt.astimezone(ZoneInfo(timezone)).isoformat()


def parse_utc_datetime(dt_string: str) -> datetime:
    """Parse a datetime string and return it as UTC.

    Args:
        dt_string: ISO formatted datetime string.

    Returns:
        datetime: The parsed datetime in UTC timezone.
    """
    dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    return to_utc(dt)


def get_timezone_offset(timezone: str) -> str:
    """Get the current UTC offset for a timezone.

    Args:
        timezone: The timezone (IANA identifier).

    Returns:
        str: The UTC offset in format '+HH:MM' or '-HH:MM'.
    """
    now = get_utc_now()
    local_time = to_local(now, timezone)
    offset = local_time.strftime('%z')
    return f"{offset[:3]}:{offset[3:]}" if len(offset) == 5 else offset


def is_dst_active(timezone: str) -> bool:
    """Check if daylight saving time is currently active in a timezone.

    Args:
        timezone: The timezone (IANA identifier).

    Returns:
        bool: True if DST is active, False otherwise.
    """
    now = get_utc_now()
    local_time = to_local(now, timezone)
    return local_time.dst().total_seconds() != 0


def get_prayer_timezone(user_timezone: Optional[str]) -> str:
    """Get the timezone to use for prayer calculations.

    Args:
        user_timezone: The user's timezone preference.

    Returns:
        str: The timezone to use for prayer calculations.
    """
    return user_timezone or 'UTC'


def validate_timezone(timezone: str) -> bool:
    """Validate if a timezone string is valid.

    Args:
        timezone: The timezone string to validate.

    Returns:
        bool: True if the timezone is valid, False otherwise.
    """
    try:
        ZoneInfo(timezone)
        return True
    except Exception:
        return False


class TimezoneMixin:
    """Mixin class to provide timezone utility methods to models."""

    def get_user_timezone(self) -> str:
        """Get the user's timezone from the model.

        This method should be overridden by models that have a user relationship.

        Returns:
            str: The user's timezone or 'UTC' as default.
        """
        return 'UTC'

    def to_utc_datetime(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Convert a datetime to UTC.

        Args:
            dt: The datetime to convert.

        Returns:
            datetime: The datetime in UTC, or None if dt is None.
        """
        if dt is None:
            return None
        return to_utc(dt)

    def to_local_datetime(self, dt: Optional[datetime]) -> Optional[datetime]:
        """Convert a UTC datetime to the user's local timezone.

        Args:
            dt: The UTC datetime to convert.

        Returns:
            datetime: The datetime in user's timezone, or None if dt is None.
        """
        if dt is None:
            return None
        return to_local(dt, self.get_user_timezone())

    def format_utc_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Format a datetime as ISO string in UTC.

        Args:
            dt: The datetime to format.

        Returns:
            str: ISO formatted datetime string in UTC, or None if dt is None.
        """
        return format_datetime_utc(dt)

    def format_local_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Format a datetime as ISO string in the user's timezone.

        Args:
            dt: The datetime to format.

        Returns:
            str: ISO formatted datetime string in user's timezone, or None if dt is None.
        """
        return format_datetime_local(dt, self.get_user_timezone())
