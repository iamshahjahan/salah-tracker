"""API helper utilities for the Salah Tracker application.

This module provides helper functions for making API requests, handling responses,
and managing external API integrations with proper error handling and retry logic.
"""

import time
from typing import Any, Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_api_request(url: str, method: str = 'GET', params: Optional[Dict[str, Any]] = None,
                    data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                    timeout: int = 10, max_retries: int = 3) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Make HTTP API request with retry logic and error handling.

    Args:
        url: API endpoint URL.
        method: HTTP method (GET, POST, PUT, DELETE).
        params: Query parameters.
        data: Request body data.
        headers: Request headers.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]], Optional[str]]: (success, response_data, error_message)
    """
    try:
        # Create session with retry strategy
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Make request
        response = session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=timeout
        )

        # Check response status
        response.raise_for_status()

        # Parse JSON response
        try:
            response_data = response.json()
        except ValueError:
            response_data = {'content': response.text}

        return True, response_data, None

    except requests.exceptions.Timeout:
        return False, None, "Request timeout"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection error"
    except requests.exceptions.HTTPError as e:
        return False, None, f"HTTP error: {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, None, f"Request error: {e!s}"
    except Exception as e:
        return False, None, f"Unexpected error: {e!s}"


def handle_api_response(response_data: Dict[str, Any], expected_keys: Optional[list] = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Handle and validate API response data.

    Args:
        response_data: API response data.
        expected_keys: List of expected keys in response.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]], Optional[str]]: (is_valid, processed_data, error_message)
    """
    try:
        if not isinstance(response_data, dict):
            return False, None, "Invalid response format"

        # Check for expected keys
        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in response_data]
            if missing_keys:
                return False, None, f"Missing required keys: {', '.join(missing_keys)}"

        # Check for error indicators in response
        if 'error' in response_data:
            return False, None, f"API error: {response_data['error']}"

        if 'status' in response_data and response_data['status'] != 'OK':
            return False, None, f"API returned non-OK status: {response_data['status']}"

        return True, response_data, None

    except Exception as e:
        return False, None, f"Error processing response: {e!s}"


def fetch_prayer_times(latitude: float, longitude: float, date_str: str,
                      timezone: str, api_key: str = "", base_url: str = "http://api.aladhan.com/v1") -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Fetch prayer times from external API.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        date_str: Date string in DD-MM-YYYY format.
        timezone: User's timezone.
        api_key: API key (optional for some services).
        base_url: Base URL for the prayer times API.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]], Optional[str]]: (success, prayer_times, error_message)
    """
    try:
        url = f"{base_url}/timings/{date_str}"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'method': 2,  # Islamic Society of North America
            'timezone': timezone
        }

        if api_key:
            params['api_key'] = api_key

        success, response_data, error = make_api_request(url, params=params)

        if not success:
            return False, None, error

        # Validate response structure
        is_valid, processed_data, validation_error = handle_api_response(
            response_data,
            expected_keys=['data']
        )

        if not is_valid:
            return False, None, validation_error

        # Extract prayer times
        timings = processed_data.get('data', {}).get('timings', {})

        if not timings:
            return False, None, "No prayer times found in response"

        return True, timings, None

    except Exception as e:
        return False, None, f"Error fetching prayer times: {e!s}"


def fetch_city_from_coordinates(latitude: float, longitude: float,
                               api_key: str = "", base_url: str = "https://api.bigdatacloud.net/data") -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Fetch city information from coordinates using geocoding API.

    Args:
        latitude: Latitude coordinate.
        longitude: Longitude coordinate.
        api_key: API key (optional for some services).
        base_url: Base URL for the geocoding API.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]], Optional[str]]: (success, city_info, error_message)
    """
    try:
        url = f"{base_url}/reverse-geocode"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'localityLanguage': 'en'
        }

        if api_key:
            params['api_key'] = api_key

        success, response_data, error = make_api_request(url, params=params)

        if not success:
            return False, None, error

        # Validate response structure
        is_valid, processed_data, validation_error = handle_api_response(response_data)

        if not is_valid:
            return False, None, validation_error

        # Extract city information
        city_info = {
            'city': processed_data.get('city', 'Unknown'),
            'country': processed_data.get('countryName', 'Unknown'),
            'timezone': processed_data.get('timezone', {}).get('name', 'UTC')
        }

        return True, city_info, None

    except Exception as e:
        return False, None, f"Error fetching city information: {e!s}"


def validate_api_credentials(api_key: str, service: str) -> bool:
    """Validate API credentials for a service.

    Args:
        api_key: API key to validate.
        service: Service name (e.g., 'prayer_times', 'geocoding').

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    if not api_key:
        return False

    if not isinstance(api_key, str):
        return False

    if len(api_key.strip()) < 5:
        return False

    # Add service-specific validation if needed
    if service == 'prayer_times':
        # Prayer times API might have specific key format requirements
        return len(api_key) >= 10
    if service == 'geocoding':
        # Geocoding API might have different requirements
        return len(api_key) >= 8

    return True


def get_api_rate_limit_info(response_headers: Dict[str, str]) -> Dict[str, Any]:
    """Extract rate limit information from API response headers.

    Args:
        response_headers: HTTP response headers.

    Returns:
        Dict[str, Any]: Rate limit information.
    """
    rate_limit_info = {}

    # Common rate limit header patterns
    rate_limit_headers = {
        'X-RateLimit-Limit': 'limit',
        'X-RateLimit-Remaining': 'remaining',
        'X-RateLimit-Reset': 'reset',
        'X-RateLimit-Reset-After': 'reset_after',
        'Retry-After': 'retry_after'
    }

    for header_name, info_key in rate_limit_headers.items():
        if header_name in response_headers:
            try:
                rate_limit_info[info_key] = int(response_headers[header_name])
            except ValueError:
                rate_limit_info[info_key] = response_headers[header_name]

    return rate_limit_info


def should_retry_request(response_status: int, response_headers: Dict[str, str]) -> Tuple[bool, Optional[int]]:
    """Determine if a request should be retried based on response.

    Args:
        response_status: HTTP response status code.
        response_headers: HTTP response headers.

    Returns:
        Tuple[bool, Optional[int]]: (should_retry, retry_after_seconds)
    """
    # Retry on server errors
    if 500 <= response_status < 600:
        return True, None

    # Retry on rate limiting
    if response_status == 429:
        retry_after = response_headers.get('Retry-After')
        if retry_after:
            try:
                return True, int(retry_after)
            except ValueError:
                return True, 60  # Default 60 seconds
        return True, 60

    # Retry on temporary redirects
    if response_status in [301, 302, 303, 307, 308]:
        return True, None

    return False, None


def log_api_request(url: str, method: str, status_code: int, response_time: float,
                   error: Optional[str] = None) -> None:
    """Log API request details for monitoring and debugging.

    Args:
        url: Request URL.
        method: HTTP method.
        status_code: Response status code.
        response_time: Response time in seconds.
        error: Error message if request failed.
    """
    import logging

    logger = logging.getLogger(__name__)

    log_data = {
        'url': url,
        'method': method,
        'status_code': status_code,
        'response_time': response_time,
        'error': error
    }

    if error:
        logger.error(f"API request failed: {log_data}")
    else:
        logger.info(f"API request completed: {log_data}")


def create_api_error_response(error_message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create standardized API error response.

    Args:
        error_message: Error message.
        status_code: HTTP status code.

    Returns:
        Dict[str, Any]: Standardized error response.
    """
    return {
        'success': False,
        'error': error_message,
        'status_code': status_code,
        'timestamp': time.time()
    }
