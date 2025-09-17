"""Prayer service for managing prayer times, completions, and Qada tracking.

This service handles prayer time calculations, completion tracking, automatic
status updates, and Qada marking with proper time validation.
"""


import hashlib
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pytz
import requests

from app.config.settings import Config
from app.models.prayer import (
    Prayer,
    PrayerCompletion,
    PrayerCompletionStatus,
    PrayerStatus,
)
from app.models.user import User

from .base_service import BaseService
from .cache_service import cache_service


def _get_status_color_and_text(prayer_status: PrayerStatus, completion: PrayerCompletion) -> Tuple[str, str]:
    """Get color for prayer status.

    Args:
        prayer_status: Prayer status string.
        completion: Prayer completion object.

    Returns:
        str: Color class name.
    """
    if completion is not None:
        # todo handle this
        if completion.status == PrayerCompletionStatus.JAMAAT or completion.status == PrayerCompletionStatus.WITHOUT_JAMAAT:
            return 'green', 'Completed'
        if completion.status == PrayerCompletionStatus.MISSED:
            return 'red', "Missed"
        if completion.status == PrayerCompletionStatus.QADA:
            return 'yellow', "Qada"

    if prayer_status == PrayerStatus.FUTURE:
        return 'gray', "Future"

    if prayer_status == PrayerStatus.MISSED:
        return 'red', PrayerStatus.MISSED.value
    return 'blue', PrayerStatus.ONGOING.value


class PrayerService(BaseService):
    """Service for managing prayer times and completions.

    This service provides methods for fetching prayer times, managing prayer
    completions, handling Qada marking, and automatic status updates.
    """


    def __init__(self, config: Optional[Config] = None):
        """Initialize the prayer service.

        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        # Get the proper config object
        if hasattr(self.config, 'EXTERNAL_API_CONFIG'):
            self.api_config = self.config.EXTERNAL_API_CONFIG
            self.prayer_time_window = self.config.PRAYER_TIME_WINDOW_MINUTES
        else:
            # Fallback to get config directly
            from app.config.settings import get_config
            config_obj = get_config()
            self.api_config = config_obj.EXTERNAL_API_CONFIG
            self.prayer_time_window = config_obj.PRAYER_TIME_WINDOW_MINUTES

        # Cache TTL settings
        self._cache_ttl = 300  # 5 minutes in seconds
        self._api_cache_ttl = 86400  # 24 hours for API responses (prayer times for a day)

    def get_prayer_times(self, user_id: int, date_str: Optional[str] = None, current_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get prayer times for a user on a specific date.

        Args:
            user_id: ID of the user.
            date_str: Date string in YYYY-MM-DD format. If None, uses today.
            current_time: Current datetime in user's timezone (required for testing).

        Returns:
            Dict[str, Any]: Prayer times data with completion status and validation info.
        """
        try:
            # Get user first (needed for timezone-aware date determination)
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Parse date
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid date format. Use YYYY-MM-DD'
                    }
            else:
                # Use current_time for date determination
                target_date = current_time.date()

            # Check if date is before user account creation
            # TODO: Along with date, I need to consider time as well.
            if target_date < user.created_at.date():
                return {
                    'success': False,
                    'error': 'Cannot access prayer times before account creation'
                }

            # Get or create prayers for the date
            prayers = self._get_or_create_prayers(user, target_date)

            # Auto-update prayer statuses
            self._auto_update_prayer_status(user, prayers, target_date,current_time)

            # Get prayer data with completion info (time-sensitive data calculated fresh each time)
            prayer_data = []
            for prayer in prayers:
                completion = self._get_prayer_completion(prayer.id)
                prayer_info = self._build_prayer_info(prayer, completion, user, target_date, current_time)
                prayer_data.append(prayer_info)

            return {
                'success': True,
                'prayers': prayer_data,
                'date': target_date.strftime('%Y-%m-%d'),
                'user_timezone': user.timezone
            }

            # Note: We don't cache the final result anymore since it contains time-sensitive data
            # The API response caching is handled separately in the route layer


        except Exception as e:
            return self.handle_service_error(e, 'get_prayer_times')

    def _get_cache_key_components(self, user: User, current_date: date) -> Tuple[str, str, str, str]:
        """Generate cache key components for prayer times.

        Args:
            user: User instance.
            current_date: Date for prayer times.

        Returns:
            Tuple of (user_id, date_str, fiqh_method, geo_hash).
        """
        user_id = str(user.id)
        date_str = current_date.strftime('%Y-%m-%d')
        fiqh_method = str(user.fiqh_method or 2)  # Default to ISNA method
        geo_hash = self._generate_geo_hash(user.location_lat or 0.0, user.location_lng or 0.0)

        return user_id, date_str, fiqh_method, geo_hash

    def _get_cached_api_response(self, user: User, current_date: date) -> Optional[Dict[str, Any]]:
        """Get cached API response for prayer times.

        Args:
            user: User instance.
            current_date: Date for prayer times.

        Returns:
            Cached API response or None if not cached.
        """
        user_id, date_str, fiqh_method, geo_hash = self._get_cache_key_components(user, current_date)
        return cache_service.get_api_prayer_times(user_id, date_str, fiqh_method, geo_hash)

    def _cache_api_response(self, user: User, current_date: date, api_response: Dict[str, Any]) -> bool:
        """Cache API response for prayer times.

        Args:
            user: User instance.
            current_date: Date for prayer times.
            api_response: API response data.

        Returns:
            True if cached successfully.
        """
        user_id, date_str, fiqh_method, geo_hash = self._get_cache_key_components(user, current_date)
        return cache_service.set_api_prayer_times(user_id, date_str, fiqh_method, geo_hash, api_response, self._api_cache_ttl)

    def _generate_geo_hash(self, latitude: float, longitude: float, precision: int = 4) -> str:
        """Generate a geo hash from latitude and longitude coordinates.

        Args:
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.
            precision: Number of decimal places for rounding (default: 4).

        Returns:
            String hash of the coordinates.
        """
        # Round coordinates to specified precision to group nearby locations
        rounded_lat = round(latitude, precision)
        rounded_lng = round(longitude, precision)

        # Create a string representation and hash it
        coord_string = f"{rounded_lat},{rounded_lng}"
        return hashlib.md5(coord_string.encode()).hexdigest()[:8]  # 8 character hash

    def complete_prayer(self, user_id: int, prayer_id: int, current_time: datetime) -> Dict[str, Any]:
        """Mark a prayer as completed with time validation.

        Args:
            user_id: ID of the user completing the prayer.
            prayer_id: ID of the prayer to complete.
            current_time: Current datetime for validation.

        Returns:
            Dict[str, Any]: Completion result with success status or error.
        """
        try:
            self.logger.info(f"Starting complete_prayer for user_id={user_id}, prayer_id={prayer_id}, current_time={current_time}")

            # Get prayer
            prayer = self.get_record_by_id(Prayer, prayer_id)
            if not prayer:
                self.logger.warning(f"Prayer not found: prayer_id={prayer_id}")
                return {
                    'success': False,
                    'error': 'Prayer not found'
                }

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                self.logger.warning(f"User not found: user_id={user_id}")
                return {
                    'success': False,
                    'error': 'User not found'
                }

            self.logger.info(f"Found prayer: {prayer.prayer_type.value} on {prayer.prayer_date} for user {user.email}")

            # Check if already completed
            existing_completion = self._get_prayer_completion(prayer_id)
            self.logger.info(f"Existing completion found: {existing_completion is not None}")
            if existing_completion:
                self.logger.warning(f"Prayer already completed: prayer_id={prayer_id}, status={existing_completion.status}")
                return {
                    'success': False,
                    'error': 'Prayer already completed'
                }

            # Validate prayer time
            self.logger.info(f"Validating prayer time for prayer {prayer_id}")
            is_valid, is_late = self._validate_prayer_time(prayer, user, current_time)
            self.logger.info(f"Prayer time validation result: is_valid={is_valid}, is_late={is_late}")

            if not is_valid and not is_late:
                self.logger.warning(f"Prayer time has not started yet: prayer_id={prayer_id}")
                return {
                    'success': False,
                    'error': 'Prayer time has not started yet'
                }

            # Determine status based on timing
            if is_late:
                status = PrayerCompletionStatus.MISSED
                marked_at = None  # No timestamp for missed prayers
                self.logger.info(f"Prayer marked as MISSED (late completion): prayer_id={prayer_id}")
            else:
                status = PrayerCompletionStatus.JAMAAT
                marked_at = datetime.now(pytz.UTC)
                self.logger.info(f"Prayer marked as JAMAAT (on-time completion): prayer_id={prayer_id}")

            # Create completion record
            self.logger.info(f"Creating completion record for prayer {prayer_id}")
            completion = self.create_record(
                PrayerCompletion,
                prayer_id=prayer_id,
                user_id=user_id,
                marked_at=marked_at,
                status=status
            )

            self.logger.info(f"Prayer completed successfully: {prayer.prayer_type.value} for user {user.email}")

            # Invalidate cache for dashboard and calendar (prayer times are no longer cached)
            cache_service.invalidate_dashboard_stats(user_id)
            cache_service.invalidate_user_calendar(user_id)

            return {
                'success': True,
                'completion': completion.to_dict(),
                'message': 'Prayer completed successfully'
            }

        except Exception as e:
            self.logger.error(f"Exception in complete_prayer: {type(e).__name__}: {e}")
            return self.handle_service_error(e, 'complete_prayer')

    def mark_prayer_qada(self, user_id: int, prayer_id: int, current_time: datetime) -> Dict[str, Any]:
        """Mark a missed prayer as Qada.

        Args:
            user_id: ID of the user marking the prayer as Qada.
            prayer_id: ID of the prayer to mark as Qada.
            current_time: Current datetime for validation.

        Returns:
            Dict[str, Any]: Qada marking result with success status or error.
        """
        try:
            self.logger.info(f"Starting mark_prayer_qada for user_id={user_id}, prayer_id={prayer_id}, current_time={current_time}")

            # Get prayer
            prayer = self.get_record_by_id(Prayer, prayer_id)
            if not prayer:
                self.logger.warning(f"Prayer not found: prayer_id={prayer_id}")
                return {
                    'success': False,
                    'error': 'Prayer not found'
                }

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                self.logger.warning(f"User not found: user_id={user_id}")
                return {
                    'success': False,
                    'error': 'User not found'
                }

            self.logger.info(f"Found prayer: {prayer.prayer_type.value} on {prayer.prayer_date} for user {user.email}")

            # Check if date is before user account creation
            if prayer.prayer_date < user.created_at.date():
                self.logger.warning(f"Cannot mark prayer as Qada before account creation: prayer_date={prayer.prayer_date}, user_created={user.created_at.date()}")
                return {
                    'success': False,
                    'error': 'Cannot mark prayers as Qada before account creation'
                }

            # Get existing completion
            existing_completion = self._get_prayer_completion(prayer_id)
            self.logger.info(f"Existing completion found: {existing_completion is not None}")

            if existing_completion:
                # Update existing completion to Qada (only from MISSED status)
                if existing_completion.status == PrayerCompletionStatus.MISSED:
                    self.logger.info(f"Updating existing MISSED completion to QADA for prayer {prayer_id}")
                    existing_completion = self.update_record(
                        existing_completion,
                        status=PrayerCompletionStatus.QADA,
                        marked_at=datetime.now(pytz.UTC)
                    )
                    completion = existing_completion
                else:
                    self.logger.warning(f"Cannot mark prayer as Qada - current status is {existing_completion.status}")
                    return {
                        'success': False,
                        'error': 'Can only mark missed prayers as Qada'
                    }
            else:
                self.logger.info("Building prayer info to check if can mark as Qada")
                prayer_info = self._build_prayer_info(prayer, None, user, prayer.prayer_date, current_time)

                if not prayer_info['can_mark_qada']:
                    self.logger.warning(f"Cannot mark prayer as Qada - prayer_info: {prayer_info}")
                    return {
                        'success': False,
                        'error': 'Can not mark as Qada'
                    }

                # Create new Qada completion
                self.logger.info(f"Creating new QADA completion for prayer {prayer_id}")
                completion = self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer_id,
                    user_id=user_id,
                    marked_at=datetime.now(pytz.UTC),
                    status=PrayerCompletionStatus.QADA
                )

            self.logger.info(f"Prayer marked as Qada successfully: {prayer.prayer_type.value} for user {user.email}")

            # Invalidate cache for dashboard and calendar (prayer times are no longer cached)
            cache_service.invalidate_dashboard_stats(user_id)
            cache_service.invalidate_user_calendar(user_id)

            return {
                'success': True,
                'completion': completion.to_dict(),
                'message': 'Prayer marked as Qada successfully'
            }

        except Exception as e:
            self.logger.error(f"Exception in mark_prayer_qada: {type(e).__name__}: {e}")
            return self.handle_service_error(e, 'mark_prayer_qada')

    def auto_update_prayer_status(self, user_id: int, current_time) -> Dict[str, Any]:
        """Automatically update prayer statuses for a user.

        Args:
            user_id: ID of the user to update prayer statuses for.
            current_time: Current datetime for status calculation.

        Returns:
            Dict[str, Any]: Update result with success status and updated count.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            today = datetime.now().date()
            prayers = self._get_prayers_for_date(user, today)

            updated_count = 0
            for prayer in prayers:
                if self._auto_update_single_prayer(prayer, user, current_time):
                    updated_count += 1

            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Updated {updated_count} prayer statuses'
            }

        except Exception as e:
            return self.handle_service_error(e, 'auto_update_prayer_status')

    def _get_or_create_prayers(self, user: User, target_date: date) -> List[Prayer]:
        """Get existing prayers for a date or create new ones if they don't exist.

        Args:
            user: User instance.
            target_date: Date to get prayers for.

        Returns:
            List[Prayer]: List of prayer instances for the date.
        """
        # Check if prayers already exist for this date
        existing_prayers = Prayer.query.filter_by(
            user_id=user.id,
            prayer_date=target_date
        ).all()

        if existing_prayers:
            return existing_prayers

        # Fetch prayer times from API
        prayer_times = self._fetch_prayer_times_from_api(user, target_date)
        if not prayer_times:
            # If API fails, try to get existing prayers from database for any date
            # This provides fallback prayer times when API is unavailable
            fallback_prayers = Prayer.query.filter_by(user_id=user.id).order_by(Prayer.prayer_date.desc()).limit(5).all()
            if fallback_prayers:
                self.logger.info(f"API unavailable, using fallback prayer times from {fallback_prayers[0].prayer_date}")
                return fallback_prayers
            return []

        # Create prayer records
        prayers = []
        for prayer_name, prayer_time in prayer_times.items():
            # Only create prayer records for the 5 main prayers, not sunrise
            if prayer_name in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                prayer = self.create_record(
                    Prayer,
                    user_id=user.id,
                    prayer_type=prayer_name,
                    prayer_time=prayer_time,
                    prayer_date=target_date
                )
                prayers.append(prayer)

        return prayers

    # TODO: Consider breaking down this complex function
    def _get_all_prayer_times_for_date(self, user: User, current_date: date) -> Dict[str, datetime.time]:
        """Get all prayer times for a date including sunrise from API.

        Args:
            user: User instance.
            current_date: Date to get prayer times for.

        Returns:
            Dict[str, datetime.time]: Dictionary with all prayer times including sunrise.
        """
        try:
            # Fetch prayer times from API
            prayer_times = self._fetch_prayer_times_from_api(user, current_date)

            # Also get prayers from database for this date
            prayers = Prayer.query.filter_by(
                user_id=user.id,
                prayer_date=current_date
            ).all()

            # Create a complete mapping
            all_times = {}

            # Add API times (including sunrise if available)
            for name, time in prayer_times.items():
                # Ensure time is a datetime.time object
                if isinstance(time, str):
                    # Handle different time formats
                    if ':' in time:
                        if time.count(':') == 1:  # HH:MM format
                            time_obj = datetime.strptime(time, '%H:%M').time()
                        elif time.count(':') == 2:  # HH:MM:SS format
                            time_obj = datetime.strptime(time, '%H:%M:%S').time()
                        else:
                            self.logger.warning(f"Unexpected time format: {time}")
                            continue
                    else:
                        self.logger.warning(f"Invalid time format: {time}")
                        continue
                else:
                    time_obj = time
                all_times[name] = time_obj

            # Add database prayer times (these should match API times)
            for prayer in prayers:
                # Ensure prayer_time is a datetime.time object
                if isinstance(prayer.prayer_time, str):
                    # Handle different time formats
                    if ':' in prayer.prayer_time:
                        if prayer.prayer_time.count(':') == 1:  # HH:MM format
                            prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M').time()
                        elif prayer.prayer_time.count(':') == 2:  # HH:MM:SS format
                            prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M:%S').time()
                        else:
                            self.logger.warning(f"Unexpected prayer time format: {prayer.prayer_time}")
                            continue
                    else:
                        self.logger.warning(f"Invalid prayer time format: {prayer.prayer_time}")
                        continue
                else:
                    prayer_time_obj = prayer.prayer_time
                all_times[prayer.prayer_type.value] = prayer_time_obj

            # If API failed and we have no prayers for this date, try to get fallback prayers
            if not prayer_times and not prayers:
                fallback_prayers = Prayer.query.filter_by(user_id=user.id).order_by(Prayer.prayer_date.desc()).limit(5).all()
                for prayer in fallback_prayers:
                    # Ensure prayer_time is a datetime.time object
                    if isinstance(prayer.prayer_time, str):
                        # Handle different time formats
                        if ':' in prayer.prayer_time:
                            if prayer.prayer_time.count(':') == 1:  # HH:MM format
                                prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M').time()
                            elif prayer.prayer_time.count(':') == 2:  # HH:MM:SS format
                                prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M:%S').time()
                            else:
                                self.logger.warning(f"Unexpected fallback prayer time format: {prayer.prayer_time}")
                                continue
                        else:
                            self.logger.warning(f"Invalid fallback prayer time format: {prayer.prayer_time}")
                            continue
                    else:
                        prayer_time_obj = prayer.prayer_time
                    all_times[prayer.prayer_type.value] = prayer_time_obj

            return all_times

        except Exception as e:
            self.logger.error(f"Error getting all prayer times for date: {e!s}")
            return {}

    def _fetch_prayer_times_from_api(self, user: User, target_date: date) -> Dict[str, datetime.time]:
        """Fetch prayer times from external API with caching.

        Args:
            user: User instance with location data.
            target_date: Date to fetch prayer times for.

        Returns:
            Dict[str, datetime.time]: Dictionary mapping prayer names to times.
        """
        try:
            # Check API response cache first (24-hour cache for API responses)
            cached_api_response = self._get_cached_api_response(user, target_date)
            if cached_api_response:
                self.logger.info(f"Using cached API response for user {user.id} on {target_date}")
                return self._parse_api_response_to_times(cached_api_response)

            if not user.location_lat or not user.location_lng:
                self.logger.warning(f"No location data for user {user.email}")
                return {}

            # Format date for API
            date_str = target_date.strftime('%d-%m-%Y')

            # Build API URL
            url = f"{self.api_config.prayer_times_base_url}/timings/{date_str}"
            params = {
                'latitude': user.location_lat,
                'longitude': user.location_lng,
                'method': user.fiqh_method or 2,  # Use user's fiqh method or default to ISNA
                'timezone': user.timezone
            }

            self.logger.info(f"Fetching prayer times from API for user {user.id} on {target_date}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Cache the full API response for 24 hours
            self._cache_api_response(user, target_date, data)

            # Parse prayer times from the response
            prayer_times = self._parse_api_response_to_times(data)
            self.logger.info(f"Cached API response for user {user.id} on {target_date}")

            return prayer_times

        except Exception as e:
            self.logger.error(f"Error fetching prayer times from API: {e!s}")
            return {}

    def _parse_api_response_to_times(self, data: Dict[str, Any]) -> Dict[str, datetime.time]:
        """Parse API response data to extract prayer times.

        Args:
            data: API response data.

        Returns:
            Dictionary mapping prayer names to times.
        """
        timings = data.get('data', {}).get('timings', {})

        # Parse prayer times
        prayer_times = {}
        prayer_names = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

        for prayer_name in prayer_names:
            if prayer_name in timings:
                time_str = timings[prayer_name]
                prayer_time = datetime.strptime(time_str, '%H:%M').time()
                prayer_times[prayer_name] = prayer_time

        # Also get sunrise time if available (for Fajr end time)
        if 'Sunrise' in timings:
            sunrise_str = timings['Sunrise']
            sunrise_time = datetime.strptime(sunrise_str, '%H:%M').time()
            prayer_times['Sunrise'] = sunrise_time

        return prayer_times

    def _get_prayer_completion(self, prayer_id: int) -> Optional[PrayerCompletion]:
        """Get prayer completion record for a prayer.

        Args:
            prayer_id: ID of the prayer.

        Returns:
            Optional[PrayerCompletion]: Completion record if found, None otherwise.
        """
        try:
            return PrayerCompletion.query.filter_by(prayer_id=prayer_id).first()
        except Exception as e:
            self.logger.error(f"Error getting prayer completion for prayer {prayer_id}: {e!s}")
            return None

    def _get_prayers_for_date(self, user: User, current_date: date) -> List[Prayer]:
        """Get all prayers for a user on a specific date.

        Args:
            user: User instance.
            current_date: Date to get prayers for.

        Returns:
            List[Prayer]: List of prayer instances.
        """
        try:
            return Prayer.query.filter_by(
                user_id=user.id,
                prayer_date=current_date
            ).all()
        except Exception as e:
            self.logger.error(f"Error getting prayers for date {current_date}: {e!s}")
            return []

    def _build_prayer_info(self, prayer: Prayer, completion: Optional[PrayerCompletion],
                           _user: User, _prayer_date: date, current_time: datetime) -> Dict[str, Any]:
        """Build prayer information dictionary with completion status and validation.

        Args:
            prayer: Prayer instance.
            completion: Prayer completion instance if exists.
            user: User instance.
            prayer_date: Date of the prayer.
            current_time: Current datetime in user's timezone.

        Returns:
            Dict[str, Any]: Prayer information dictionary.
        """
        # Get prayer time status
        prayer_status, start_time, end_time = self._get_prayer_time_status(prayer, current_time)

        status_color, status_text = _get_status_color_and_text(prayer_status=prayer_status, completion=completion)

        return {
            'id': prayer.id,
            'prayer_type': prayer.prayer_type.value,
            'prayer_time': prayer.prayer_time.strftime('%H:%M'),
            'completed': (completion is not None),
            'can_complete': (completion is None) and (prayer_status in [PrayerStatus.ONGOING, PrayerStatus.MISSED]),
            'is_missed': prayer_status == PrayerStatus.MISSED,
            'can_mark_qada': (completion is None) and (prayer_status == PrayerStatus.MISSED),
            'is_late': prayer_status == PrayerStatus.MISSED,
            'completion': completion.to_dict() if completion else None,
            'prayer_status': prayer_status.value,
            'status_color': status_color,
            'status_text': status_text,
            'time_window': {
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'start_datetime': start_time.isoformat(),
                'end_datetime': end_time.isoformat()
            },
            'current_time': current_time.strftime('%H:%M'),
        }


    def _validate_prayer_time(self, prayer: Prayer, _user: User, current_time) -> Tuple[bool, bool]:
        """Validate if a prayer can be completed at the current time.

        Args:
            prayer: Prayer instance.
            user: User instance.
            current_time: Current datetime for validation.

        Returns:
            Tuple[bool, bool]: (can_complete, is_late) - whether prayer can be completed and if it's late.
        """
        try:
            self.logger.debug(f"Validating prayer time for prayer {prayer.id}: {prayer.prayer_type.value}")

            # Calculate prayer time window using the same logic as the route
            start_time, end_time = self._get_prayer_time_window(prayer)

            self.logger.debug(f"Prayer {prayer.id} validation - time window: start={start_time}, end={end_time}")
            self.logger.debug(f"Prayer {prayer.id} validation - current_time before normalization: {current_time}")

            # Ensure current_time is timezone-aware and in the same timezone as start_time/end_time
            if current_time.tzinfo is None:
                # If current_time is naive, assume it's in the user's timezone
                user_tz = pytz.timezone(prayer.user.timezone)
                current_time = user_tz.localize(current_time)
                self.logger.debug(f"Prayer {prayer.id} validation - localized naive current_time: {current_time}")
            elif current_time.tzinfo != start_time.tzinfo:
                # If timezones don't match, convert current_time to the same timezone as start_time
                current_time = current_time.astimezone(start_time.tzinfo)
                self.logger.debug(f"Prayer {prayer.id} validation - converted current_time timezone: {current_time}")

            self.logger.debug(f"Prayer {prayer.id} validation - final current_time: {current_time}")

            # Check if current time is within prayer window
            if current_time < start_time:
                self.logger.debug(f"Prayer {prayer.id} validation - too early (current < start)")
                return False, False  # Too early
            if current_time <= end_time:
                self.logger.debug(f"Prayer {prayer.id} validation - on time (current <= end)")
                return True, False   # On time
            self.logger.debug(f"Prayer {prayer.id} validation - too late (current > end)")
            return False, False  # Too late - cannot complete during window

        except Exception as e:
            self.logger.error(f"Error validating prayer time for prayer {prayer.id}: {type(e).__name__}: {e}")
            self.logger.error(f"Prayer details: type={prayer.prayer_type}, date={prayer.prayer_date}, time={prayer.prayer_time}")
            self.logger.error(f"User timezone: {prayer.user.timezone}")
            self.logger.error(f"Current time: {current_time}")
            return False, False

    # TODO: Consider breaking down this complex function
    def _get_prayer_time_window(self, prayer: Prayer) -> Tuple[datetime, datetime]:
        """Get the valid time window for completing a prayer using Islamic methodology.

        Each prayer ends when the next prayer begins.

        Args:
            prayer: Prayer instance.

        Returns:
            Tuple[datetime, datetime]: (start_time, end_time) for the prayer window.
        """
        from app.models.prayer import PrayerType

        # Get all prayer times for the same date including sunrise
        prayer_times = self._get_all_prayer_times_for_date(prayer.user, prayer.prayer_date)

        # Get user timezone
        user_tz = pytz.timezone(prayer.user.timezone)

        # Calculate start and end times (timezone-aware)
        # Ensure prayer_time is a datetime.time object
        if isinstance(prayer.prayer_time, str):
            # Handle different time formats
            if ':' in prayer.prayer_time:
                if prayer.prayer_time.count(':') == 1:  # HH:MM format
                    prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M').time()
                elif prayer.prayer_time.count(':') == 2:  # HH:MM:SS format
                    prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M:%S').time()
                else:
                    self.logger.error(f"Unexpected prayer time format in time window: {prayer.prayer_time}")
                    # Return a default time window
                    return datetime.now(), datetime.now() + timedelta(hours=2)
            else:
                self.logger.error(f"Invalid prayer time format in time window: {prayer.prayer_time}")
                # Return a default time window
                return datetime.now(), datetime.now() + timedelta(hours=2)
        else:
            prayer_time_obj = prayer.prayer_time

        prayer_datetime = datetime.combine(prayer.prayer_date, prayer_time_obj)
        start_time = user_tz.localize(prayer_datetime)

        # Determine end time based on Islamic methodology
        if prayer.prayer_type == PrayerType.FAJR:
            # Fajr ends at Sunrise (use actual sunrise if available, otherwise Dhuhr as approximation)
            if 'Sunrise' in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times['Sunrise'])
                end_time = user_tz.localize(end_datetime)
            elif PrayerType.DHUHR in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.DHUHR.value])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 6 hours after Fajr (approximate sunrise)
                end_time = start_time + timedelta(hours=6)

        elif prayer.prayer_type == PrayerType.DHUHR:
            # Dhuhr ends at Asr
            if PrayerType.ASR in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.ASR.value])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 3 hours after Dhuhr
                end_time = start_time + timedelta(hours=3)

        elif prayer.prayer_type == PrayerType.ASR:
            # Asr ends at Maghrib
            if PrayerType.MAGHRIB in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.MAGHRIB.value])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 2 hours after Asr
                end_time = start_time + timedelta(hours=2)

        elif prayer.prayer_type == PrayerType.MAGHRIB:
            # Maghrib ends at Isha
            if PrayerType.ISHA in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.ISHA.value])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 30 minutes after Maghrib
                end_time = start_time + timedelta(minutes=30)

        elif prayer.prayer_type == PrayerType.ISHA:
            # Isha ends at next day's Fajr
            # For Isha, we need to set the end time to next day's Fajr (03:21)
            # Since Isha is typically at 19:21 and Fajr is at 05:21, we add 10 hours
            # But to be safe, let's add 8 hours and then add a day
            end_time = start_time + timedelta(hours=8, days=0)
        else:
            # Default fallback
            end_time = start_time + timedelta(hours=2)

        return start_time, end_time


    def _get_prayer_time_status(self, prayer: Prayer, current_time) -> Tuple[PrayerStatus, datetime, datetime]:
        """Get the prayer time status based on current time relative to prayer window.

        Args:
            prayer: Prayer instance.
            current_time: Current datetime for status calculation.

        Returns:
            str: Time status ('future', 'ongoing', 'missed').
        """
        try:
            # Get prayer time window
            start_time, end_time = self._get_prayer_time_window(prayer)

            self.logger.debug(f"Prayer {prayer.id} time window: start={start_time}, end={end_time}")
            self.logger.debug(f"Current time before normalization: {current_time} (tzinfo: {current_time.tzinfo})")

            # Ensure current_time is timezone-aware and in the same timezone as start_time/end_time
            if current_time.tzinfo is None:
                # If current_time is naive, assume it's in the user's timezone
                user_tz = pytz.timezone(prayer.user.timezone)
                current_time = user_tz.localize(current_time)
                self.logger.debug(f"Localized naive current_time to user timezone: {current_time}")
            elif current_time.tzinfo != start_time.tzinfo:
                # If timezones don't match, convert current_time to the same timezone as start_time
                current_time = current_time.astimezone(start_time.tzinfo)
                self.logger.debug(f"Converted current_time to match start_time timezone: {current_time}")

            self.logger.debug(f"Final current_time: {current_time} (tzinfo: {current_time.tzinfo})")
            self.logger.debug(f"Start time: {start_time} (tzinfo: {start_time.tzinfo})")
            self.logger.debug(f"End time: {end_time} (tzinfo: {end_time.tzinfo})")

            # Determine status based on current time
            if current_time < start_time:
                self.logger.debug(f"Prayer {prayer.id} status: FUTURE (current < start)")
                return PrayerStatus.FUTURE, start_time, end_time  # Before prayer start time
            if end_time >= current_time >= start_time:
                self.logger.debug(f"Prayer {prayer.id} status: ONGOING (start <= current <= end)")
                return PrayerStatus.ONGOING , start_time, end_time # Between start and end time
            self.logger.debug(f"Prayer {prayer.id} status: MISSED (current > end)")
            return PrayerStatus.MISSED, start_time, end_time  # After prayer end time

        except Exception as e:
            self.logger.error(f"Error in _get_prayer_time_status for prayer {prayer.id}: {type(e).__name__}: {e}")
            self.logger.error(f"Prayer details: type={prayer.prayer_type}, date={prayer.prayer_date}, time={prayer.prayer_time}")
            self.logger.error(f"User timezone: {prayer.user.timezone}")
            self.logger.error(f"Current time: {current_time}")
            raise


    def _can_mark_qada(self, _prayer: Prayer, completion: Optional[PrayerCompletion],
                       time_status: str, user: User, current_date: date) -> bool:
        """Check if a prayer can be marked as Qada.

        Args:
            prayer: Prayer instance.
            completion: Prayer completion instance if exists.
            time_status: Time status ('future', 'ongoing', 'missed').
            user: User instance.
            current_date: Date of the prayer.

        Returns:
            bool: True if prayer can be marked as Qada, False otherwise.
        """
        # Can't mark Qada before account creation
        if current_date < user.created_at.date():
            return False

        # Can mark Qada if prayer is missed and not completed
        if time_status == 'missed' and not completion:
            return True

        # Can mark Qada if prayer is marked as missed
        return bool(completion and completion.status == PrayerCompletionStatus.MISSED)

    def _auto_update_prayer_status(self, user: User, prayers: List[Prayer], _current_date: date, current_time) -> None:
        """Automatically update prayer statuses for a list of prayers.

        Args:
            user: User instance.
            prayers: List of prayer instances.
            current_date: Date of the prayers.
            current_time: Current datetime for status calculation.
        """
        for prayer in prayers:
            self._auto_update_single_prayer(prayer, user, current_time)

    def _auto_update_single_prayer(self, prayer: Prayer, user: User, current_time) -> bool:
        """Automatically update status for a single prayer.

        Args:
            prayer: Prayer instance.
            user: User instance.
            current_time: Current datetime for status calculation.

        Returns:
            bool: True if prayer status was updated, False otherwise.
        """
        try:
            # Check if prayer is missed and not completed
            is_missed = self._is_prayer_missed(prayer, current_time)
            existing_completion = self._get_prayer_completion(prayer.id)

            if is_missed and not existing_completion:
                # Automatically mark as missed
                self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer.id,
                    user_id=user.id,
                    marked_at=None,  # No timestamp for missed prayers
                    status=PrayerCompletionStatus.MISSED
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error auto-updating prayer {prayer.id}: {e!s}")
            return False

    def _is_prayer_missed(self, prayer: Prayer, current_time) -> bool:
        """Check if a prayer is missed based on current time.

        Args:
            prayer: Prayer instance.
            current_time: Current datetime for comparison.

        Returns:
            bool: True if prayer is missed, False otherwise.
        """
        try:
            # Get prayer time status
            time_status = self._get_prayer_time_status(prayer, current_time=current_time)
            return time_status == 'missed'
        except Exception as e:
            self.logger.error(f"Error checking if prayer is missed: {e!s}")
            return False
