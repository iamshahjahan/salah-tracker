"""
Custom exceptions for the Salah Tracker application.

This module provides custom exception classes for better error handling
and more specific error messages throughout the application.
"""

from typing import Optional, Dict, Any


class SalahRemindersException(Exception):
    """
    Base exception class for all Salah Tracker application exceptions.

    This class provides a common base for all custom exceptions with
    additional context and error code support.
    """

    def __init__(self, message: str, error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.

        Args:
            message: Error message.
            error_code: Optional error code for programmatic handling.
            context: Optional additional context information.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Returns:
            Dict[str, Any]: Exception data as dictionary.
        """
        return {
            'error': self.message,
            'error_code': self.error_code,
            'context': self.context
        }


class ValidationError(SalahRemindersException):
    """
    Exception raised for validation errors.

    This exception is raised when input validation fails,
    such as invalid email format or missing required fields.
    """

    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None):
        """
        Initialize validation error.

        Args:
            message: Validation error message.
            field: Field that failed validation.
            value: Value that failed validation.
        """
        context = {}
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)

        super().__init__(message, 'VALIDATION_ERROR', context)


class AuthenticationError(SalahRemindersException):
    """
    Exception raised for authentication errors.

    This exception is raised when authentication fails,
    such as invalid credentials or expired tokens.
    """

    def __init__(self, message: str = "Authentication failed"):
        """
        Initialize authentication error.

        Args:
            message: Authentication error message.
        """
        super().__init__(message, 'AUTHENTICATION_ERROR')


class AuthorizationError(SalahRemindersException):
    """
    Exception raised for authorization errors.

    This exception is raised when a user doesn't have permission
    to perform a specific action.
    """

    def __init__(self, message: str = "Access denied"):
        """
        Initialize authorization error.

        Args:
            message: Authorization error message.
        """
        super().__init__(message, 'AUTHORIZATION_ERROR')


class UserNotFoundError(SalahRemindersException):
    """
    Exception raised when a user is not found.

    This exception is raised when attempting to access a user
    that doesn't exist in the database.
    """

    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        """
        Initialize user not found error.

        Args:
            user_id: ID of the user that was not found.
            email: Email of the user that was not found.
        """
        context = {}
        if user_id:
            context['user_id'] = user_id
        if email:
            context['email'] = email

        message = "User not found"
        if user_id:
            message = f"User with ID {user_id} not found"
        elif email:
            message = f"User with email {email} not found"

        super().__init__(message, 'USER_NOT_FOUND', context)


class PrayerNotFoundError(SalahRemindersException):
    """
    Exception raised when a prayer is not found.

    This exception is raised when attempting to access a prayer
    that doesn't exist in the database.
    """

    def __init__(self, prayer_id: Optional[int] = None):
        """
        Initialize prayer not found error.

        Args:
            prayer_id: ID of the prayer that was not found.
        """
        context = {}
        if prayer_id:
            context['prayer_id'] = prayer_id

        message = "Prayer not found"
        if prayer_id:
            message = f"Prayer with ID {prayer_id} not found"

        super().__init__(message, 'PRAYER_NOT_FOUND', context)


class PrayerTimeError(SalahRemindersException):
    """
    Exception raised for prayer time related errors.

    This exception is raised when there are issues with prayer time
    calculations or validations.
    """

    def __init__(self, message: str, prayer_name: Optional[str] = None):
        """
        Initialize prayer time error.

        Args:
            message: Prayer time error message.
            prayer_name: Name of the prayer that caused the error.
        """
        context = {}
        if prayer_name:
            context['prayer_name'] = prayer_name

        super().__init__(message, 'PRAYER_TIME_ERROR', context)


class ExternalAPIError(SalahRemindersException):
    """
    Exception raised for external API errors.

    This exception is raised when there are issues with external API
    calls, such as prayer times API or geocoding API.
    """

    def __init__(self, message: str, api_name: Optional[str] = None,
                 status_code: Optional[int] = None):
        """
        Initialize external API error.

        Args:
            message: API error message.
            api_name: Name of the API that failed.
            status_code: HTTP status code from the API response.
        """
        context = {}
        if api_name:
            context['api_name'] = api_name
        if status_code:
            context['status_code'] = status_code

        super().__init__(message, 'EXTERNAL_API_ERROR', context)


class DatabaseError(SalahRemindersException):
    """
    Exception raised for database errors.

    This exception is raised when there are issues with database
    operations, such as connection failures or constraint violations.
    """

    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize database error.

        Args:
            message: Database error message.
            operation: Database operation that failed.
        """
        context = {}
        if operation:
            context['operation'] = operation

        super().__init__(message, 'DATABASE_ERROR', context)


class ConfigurationError(SalahRemindersException):
    """
    Exception raised for configuration errors.

    This exception is raised when there are issues with application
    configuration, such as missing environment variables.
    """

    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration error.

        Args:
            message: Configuration error message.
            config_key: Configuration key that caused the error.
        """
        context = {}
        if config_key:
            context['config_key'] = config_key

        super().__init__(message, 'CONFIGURATION_ERROR', context)


class NotificationError(SalahRemindersException):
    """
    Exception raised for notification errors.

    This exception is raised when there are issues with sending
    notifications, such as email delivery failures.
    """

    def __init__(self, message: str, notification_type: Optional[str] = None):
        """
        Initialize notification error.

        Args:
            message: Notification error message.
            notification_type: Type of notification that failed.
        """
        context = {}
        if notification_type:
            context['notification_type'] = notification_type

        super().__init__(message, 'NOTIFICATION_ERROR', context)


class RateLimitError(SalahRemindersException):
    """
    Exception raised for rate limiting errors.

    This exception is raised when API rate limits are exceeded
    or when too many requests are made in a short time period.
    """

    def __init__(self, message: str = "Rate limit exceeded",
                 retry_after: Optional[int] = None):
        """
        Initialize rate limit error.

        Args:
            message: Rate limit error message.
            retry_after: Seconds to wait before retrying.
        """
        context = {}
        if retry_after:
            context['retry_after'] = retry_after

        super().__init__(message, 'RATE_LIMIT_ERROR', context)


class BusinessLogicError(SalahRemindersException):
    """
    Exception raised for business logic errors.

    This exception is raised when business rules are violated,
    such as attempting to complete a prayer outside its time window.
    """

    def __init__(self, message: str, rule: Optional[str] = None):
        """
        Initialize business logic error.

        Args:
            message: Business logic error message.
            rule: Business rule that was violated.
        """
        context = {}
        if rule:
            context['rule'] = rule

        super().__init__(message, 'BUSINESS_LOGIC_ERROR', context)
