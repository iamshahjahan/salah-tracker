"""
Prayer service for managing prayer times, completions, and Qada tracking.

This service handles prayer time calculations, completion tracking, automatic
status updates, and Qada marking with proper time validation.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
import pytz
from dateutil import parser
import threading

from .base_service import BaseService
from .cache_service import cache_service
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerStatus
from app.config.settings import Config


class PrayerService(BaseService):
    """
    Service for managing prayer times and completions.

    This service provides methods for fetching prayer times, managing prayer
    completions, handling Qada marking, and automatic status updates.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the prayer service.

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

    def get_prayer_times(self, user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Get prayer times for a user on a specific date.

        Args:
            user_id: ID of the user.
            date_str: Date string in YYYY-MM-DD format. If None, uses today.

        Returns:
            Dict[str, Any]: Prayer times data with completion status and validation info.
        """
        try:
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
                target_date = datetime.now().date()

            # Check cache first
            cached_data = cache_service.get_prayer_times(user_id, date_str or target_date.strftime('%Y-%m-%d'))
            if cached_data:
                return cached_data

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Check if date is before user account creation
            if target_date < user.created_at.date():
                return {
                    'success': False,
                    'error': 'Cannot access prayer times before account creation'
                }

            # Get or create prayers for the date
            prayers = self._get_or_create_prayers(user, target_date)

            # Auto-update prayer statuses
            self._auto_update_prayer_status(user, prayers, target_date)

            # Get prayer data with completion info
            prayer_data = []
            for prayer in prayers:
                completion = self._get_prayer_completion(prayer.id)
                prayer_info = self._build_prayer_info(prayer, completion, user, target_date)
                prayer_data.append(prayer_info)

            result = {
                'success': True,
                'prayers': prayer_data,
                'date': target_date.strftime('%Y-%m-%d'),
                'user_timezone': user.timezone
            }

            # Cache the result
            cache_service.set_prayer_times(user_id, date_str or target_date.strftime('%Y-%m-%d'), result, self._cache_ttl)

            return result

        except Exception as e:
            return self.handle_service_error(e, 'get_prayer_times')

    def complete_prayer(self, user_id: int, prayer_id: int) -> Dict[str, Any]:
        """
        Mark a prayer as completed with time validation.

        Args:
            user_id: ID of the user completing the prayer.
            prayer_id: ID of the prayer to complete.

        Returns:
            Dict[str, Any]: Completion result with success status or error.
        """
        try:
            # Get prayer
            prayer = self.get_record_by_id(Prayer, prayer_id)
            if not prayer:
                return {
                    'success': False,
                    'error': 'Prayer not found'
                }

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Check if already completed
            existing_completion = self._get_prayer_completion(prayer_id)
            if existing_completion:
                return {
                    'success': False,
                    'error': 'Prayer already completed'
                }

            # Validate prayer time
            prayer_date = prayer.prayer_date
            is_valid, is_late = self._validate_prayer_time(prayer, user)

            if not is_valid and not is_late:
                return {
                    'success': False,
                    'error': 'Prayer time has not started yet'
                }

            # Determine status based on timing
            if is_late:
                status = PrayerStatus.MISSED
                marked_at = None  # No timestamp for missed prayers
            else:
                status = PrayerStatus.COMPLETE
                marked_at = datetime.now(datetime.timezone.utc)

            # Create completion record
            completion = self.create_record(
                PrayerCompletion,
                prayer_id=prayer_id,
                user_id=user_id,
                marked_at=marked_at,
                status=status
            )

            self.logger.info(f"Prayer completed: {prayer.prayer_type.value} for user {user.email}")

            # Invalidate cache for this user and date
            date_str = prayer.prayer_date.strftime('%Y-%m-%d')
            cache_service.invalidate_prayer_times(user_id, date_str)
            cache_service.invalidate_dashboard_stats(user_id)
            cache_service.invalidate_user_calendar(user_id)

            return {
                'success': True,
                'completion': completion.to_dict(),
                'message': 'Prayer completed successfully'
            }

        except Exception as e:
            return self.handle_service_error(e, 'complete_prayer')

    def mark_prayer_qada(self, user_id: int, prayer_id: int) -> Dict[str, Any]:
        """
        Mark a missed prayer as Qada.

        Args:
            user_id: ID of the user marking the prayer as Qada.
            prayer_id: ID of the prayer to mark as Qada.

        Returns:
            Dict[str, Any]: Qada marking result with success status or error.
        """
        try:
            # Get prayer
            prayer = self.get_record_by_id(Prayer, prayer_id)
            if not prayer:
                return {
                    'success': False,
                    'error': 'Prayer not found'
                }

            # Get user
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Check if date is before user account creation
            if prayer.prayer_date < user.created_at.date():
                return {
                    'success': False,
                    'error': 'Cannot mark prayers as Qada before account creation'
                }

            # Get existing completion
            existing_completion = self._get_prayer_completion(prayer_id)

            if existing_completion:
                # Update existing completion to Qada (only from MISSED status)
                if existing_completion.status == PrayerStatus.MISSED:
                    self.update_record(
                        existing_completion,
                        status=PrayerStatus.QADA,
                        marked_at=datetime.utcnow()
                    )
                    completion = existing_completion
                else:
                    return {
                        'success': False,
                        'error': 'Can only mark missed prayers as Qada'
                    }
            else:
                # Create new Qada completion
                completion = self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer_id,
                    user_id=user_id,
                    marked_at=datetime.now(datetime.timezone.utc),
                    status=PrayerStatus.QADA
                )

            self.logger.info(f"Prayer marked as Qada: {prayer.prayer_type.value} for user {user.email}")

            # Invalidate cache for this user and date
            date_str = prayer.prayer_date.strftime('%Y-%m-%d')
            cache_service.invalidate_prayer_times(user_id, date_str)
            cache_service.invalidate_dashboard_stats(user_id)
            cache_service.invalidate_user_calendar(user_id)

            return {
                'success': True,
                'completion': completion.to_dict(),
                'message': 'Prayer marked as Qada successfully'
            }

        except Exception as e:
            return self.handle_service_error(e, 'mark_prayer_qada')

    def auto_update_prayer_status(self, user_id: int) -> Dict[str, Any]:
        """
        Automatically update prayer statuses for a user.

        Args:
            user_id: ID of the user to update prayer statuses for.

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
                if self._auto_update_single_prayer(prayer, user, today):
                    updated_count += 1

            return {
                'success': True,
                'updated_count': updated_count,
                'message': f'Updated {updated_count} prayer statuses'
            }

        except Exception as e:
            return self.handle_service_error(e, 'auto_update_prayer_status')

    def _get_or_create_prayers(self, user: User, date: datetime.date) -> List[Prayer]:
        """
        Get existing prayers for a date or create new ones if they don't exist.

        Args:
            user: User instance.
            date: Date to get prayers for.

        Returns:
            List[Prayer]: List of prayer instances for the date.
        """
        # Check if prayers already exist for this date
        existing_prayers = Prayer.query.filter_by(
            user_id=user.id,
            prayer_date=date
        ).all()

        if existing_prayers:
            return existing_prayers

        # Fetch prayer times from API
        prayer_times = self._fetch_prayer_times_from_api(user, date)
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
                    prayer_date=date
                )
                prayers.append(prayer)

        return prayers

    def _get_all_prayer_times_for_date(self, user: User, date: datetime.date) -> Dict[str, datetime.time]:
        """
        Get all prayer times for a date including sunrise from API.
        
        Args:
            user: User instance.
            date: Date to get prayer times for.
            
        Returns:
            Dict[str, datetime.time]: Dictionary with all prayer times including sunrise.
        """
        try:
            # Fetch prayer times from API
            prayer_times = self._fetch_prayer_times_from_api(user, date)
            
            # Also get prayers from database for this date
            prayers = Prayer.query.filter_by(
                user_id=user.id,
                prayer_date=date
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
            self.logger.error(f"Error getting all prayer times for date: {str(e)}")
            return {}

    def _fetch_prayer_times_from_api(self, user: User, date: datetime.date) -> Dict[str, datetime.time]:
        """
        Fetch prayer times from external API with caching.

        Args:
            user: User instance with location data.
            date: Date to fetch prayer times for.

        Returns:
            Dict[str, datetime.time]: Dictionary mapping prayer names to times.
        """
        try:
            # Check cache first
            cached_times = cache_service.get_prayer_times(user.id, date.strftime('%Y-%m-%d'))
            if cached_times is not None:
                self.logger.info(f"Using cached prayer times for user {user.id} on {date}")
                return cached_times

            if not user.location_lat or not user.location_lng:
                self.logger.warning(f"No location data for user {user.email}")
                return {}

            # Format date for API
            date_str = date.strftime('%d-%m-%Y')

            # Build API URL
            url = f"{self.api_config.prayer_times_base_url}/timings/{date_str}"
            params = {
                'latitude': user.location_lat,
                'longitude': user.location_lng,
                'method': 2,  # Islamic Society of North America
                'timezone': user.timezone
            }

            self.logger.info(f"Fetching prayer times from API for user {user.id} on {date}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
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

            # Cache the results for 5 minutes
            if prayer_times:
                cache_service.set_prayer_times(user.id, date.strftime('%Y-%m-%d'), prayer_times, ttl_seconds=300)
                self.logger.info(f"Cached prayer times for user {user.id} on {date}")

            return prayer_times

        except Exception as e:
            self.logger.error(f"Error fetching prayer times from API: {str(e)}")
            return {}

    def _get_prayer_completion(self, prayer_id: int) -> Optional[PrayerCompletion]:
        """
        Get prayer completion record for a prayer.

        Args:
            prayer_id: ID of the prayer.

        Returns:
            Optional[PrayerCompletion]: Completion record if found, None otherwise.
        """
        try:
            return PrayerCompletion.query.filter_by(prayer_id=prayer_id).first()
        except Exception as e:
            self.logger.error(f"Error getting prayer completion for prayer {prayer_id}: {str(e)}")
            return None

    def _get_prayers_for_date(self, user: User, date: datetime.date) -> List[Prayer]:
        """
        Get all prayers for a user on a specific date.

        Args:
            user: User instance.
            date: Date to get prayers for.

        Returns:
            List[Prayer]: List of prayer instances.
        """
        try:
            return Prayer.query.filter_by(
                user_id=user.id,
                prayer_date=date
            ).all()
        except Exception as e:
            self.logger.error(f"Error getting prayers for date {date}: {str(e)}")
            return []

    def _build_prayer_info(self, prayer: Prayer, completion: Optional[PrayerCompletion],
                          user: User, date: datetime.date) -> Dict[str, Any]:
        """
        Build prayer information dictionary with completion status and validation.

        Args:
            prayer: Prayer instance.
            completion: Prayer completion instance if exists.
            user: User instance.
            date: Date of the prayer.

        Returns:
            Dict[str, Any]: Prayer information dictionary.
        """
        # Get prayer time status
        time_status = self._get_prayer_time_status(prayer, user, date)
        is_missed = (time_status == 'missed')

        # Check if prayer time is valid for completion
        can_complete, is_late = self._validate_prayer_time(prayer, user)

        # Determine if can mark as Qada
        can_mark_qada = self._can_mark_qada(prayer, completion, time_status, user, date)

        # Get prayer time window information
        start_time, end_time = self._get_prayer_time_window(prayer)
        
        # Get current time in user timezone
        user_tz = pytz.timezone(user.timezone)
        now = datetime.now(user_tz)

        # Determine prayer status (four-state system)
        prayer_status = self._get_prayer_status(completion, time_status, can_complete)
        status_color = self._get_status_color(prayer_status)
        status_text = self._get_status_text(prayer_status)

        prayer_info = {
            'id': prayer.id,
            'prayer_type': prayer.prayer_type.value,
            'prayer_time': prayer.prayer_time.strftime('%H:%M'),
            'completed': completion is not None,
            'can_complete': can_complete,
            'is_missed': is_missed,
            'can_mark_qada': can_mark_qada,
            'is_late': is_late,
            'completion': completion.to_dict() if completion else None,
            'prayer_status': prayer_status,
            'status_color': status_color,
            'status_text': status_text,
            'time_window': {
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
                'start_datetime': start_time.isoformat(),
                'end_datetime': end_time.isoformat()
            },
            'current_time': now.strftime('%H:%M'),
            'time_status': self._get_time_status(now, start_time, end_time)
        }

        return prayer_info

    def _get_prayer_status(self, completion: Optional[PrayerCompletion], time_status: str, can_complete: bool) -> str:
        """
        Determine prayer status based on completion and timing.
        
        Args:
            completion: Prayer completion instance if exists.
            time_status: Time status ('future', 'pending', 'missed').
            can_complete: Whether prayer can be completed now.
            
        Returns:
            str: Prayer status ('future', 'pending', 'missed', 'completed', 'qada').
        """
        if completion is not None:
            # Prayer has been marked
            if completion.status == PrayerStatus.QADA:
                return 'qada'  # Marked as Qada (yellow) - terminal state
            elif completion.status == PrayerStatus.COMPLETE:
                return 'completed'  # Completed within time window (green) - terminal state
            elif completion.status == PrayerStatus.PENDING:
                return 'pending'  # Marked as pending (blue) - can go to completed
            elif completion.status == PrayerStatus.MISSED:
                return 'missed'  # Marked as missed (red) - can go to qada
            elif completion.status == PrayerStatus.FUTURE:
                return 'future'  # Marked as future (gray) - waiting for prayer time
        else:
            # Prayer not marked yet - use time status
            return time_status

    def _get_status_color(self, prayer_status: str) -> str:
        """
        Get color for prayer status.
        
        Args:
            prayer_status: Prayer status string.
            
        Returns:
            str: Color class name.
        """
        color_map = {
            'future': 'gray',        # Before prayer start time
            'pending': 'blue',       # Can go to completed - within time window
            'missed': 'red',         # Can go to qada - time window passed
            'completed': 'green',    # Terminal state - completed within time window
            'qada': 'yellow'         # Terminal state - completed as qada
        }
        return color_map.get(prayer_status, 'red')

    def _get_status_text(self, prayer_status: str) -> str:
        """
        Get display text for prayer status.
        
        Args:
            prayer_status: Prayer status string.
            
        Returns:
            str: Status text to display.
        """
        text_map = {
            'future': 'Future',
            'pending': 'In Progress',
            'missed': 'Missed',
            'completed': 'Completed',
            'qada': 'Qada'
        }
        return text_map.get(prayer_status, 'Missed')

    def _get_time_status(self, current_time: datetime, start_time: datetime, end_time: datetime) -> str:
        """
        Get the current time status relative to prayer window.
        
        Args:
            current_time: Current time in user timezone.
            start_time: Prayer window start time.
            end_time: Prayer window end time.
            
        Returns:
            str: Time status ('before', 'during', 'after')
        """
        if current_time < start_time:
            return 'before'
        elif current_time <= end_time:
            return 'during'
        else:
            return 'after'

    def _validate_prayer_time(self, prayer: Prayer, user: User) -> Tuple[bool, bool]:
        """
        Validate if a prayer can be completed at the current time.

        Args:
            prayer: Prayer instance.
            user: User instance.

        Returns:
            Tuple[bool, bool]: (can_complete, is_late) - whether prayer can be completed and if it's late.
        """
        try:
            # Get user timezone
            user_tz = pytz.timezone(user.timezone)
            now = datetime.now(user_tz)

            # Get prayer time in user timezone
            # Ensure prayer_time is a datetime.time object
            if isinstance(prayer.prayer_time, str):
                # Handle different time formats
                if ':' in prayer.prayer_time:
                    if prayer.prayer_time.count(':') == 1:  # HH:MM format
                        prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M').time()
                    elif prayer.prayer_time.count(':') == 2:  # HH:MM:SS format
                        prayer_time_obj = datetime.strptime(prayer.prayer_time, '%H:%M:%S').time()
                    else:
                        self.logger.error(f"Unexpected prayer time format in validation: {prayer.prayer_time}")
                        return False, False
                else:
                    self.logger.error(f"Invalid prayer time format in validation: {prayer.prayer_time}")
                    return False, False
            else:
                prayer_time_obj = prayer.prayer_time
                
            prayer_datetime = user_tz.localize(
                datetime.combine(prayer.prayer_date, prayer_time_obj)
            )

            # Calculate prayer time window using the same logic as the route
            start_time, end_time = self._get_prayer_time_window(prayer)

            # Check if current time is within prayer window
            if now < start_time:
                return False, False  # Too early
            elif now <= end_time:
                return True, False   # On time
            else:
                return False, False  # Too late - cannot complete during window

        except Exception as e:
            self.logger.error(f"Error validating prayer time: {str(e)}")
            return False, False

    def _get_prayer_time_window(self, prayer: Prayer) -> Tuple[datetime, datetime]:
        """
        Get the valid time window for completing a prayer using Islamic methodology.
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
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.DHUHR])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 6 hours after Fajr (approximate sunrise)
                end_time = start_time + timedelta(hours=6)
                
        elif prayer.prayer_type == PrayerType.DHUHR:
            # Dhuhr ends at Asr
            if PrayerType.ASR in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.ASR])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 3 hours after Dhuhr
                end_time = start_time + timedelta(hours=3)
                
        elif prayer.prayer_type == PrayerType.ASR:
            # Asr ends at Maghrib
            if PrayerType.MAGHRIB in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.MAGHRIB])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 2 hours after Asr
                end_time = start_time + timedelta(hours=2)
                
        elif prayer.prayer_type == PrayerType.MAGHRIB:
            # Maghrib ends at Isha
            if PrayerType.ISHA in prayer_times:
                end_datetime = datetime.combine(prayer.prayer_date, prayer_times[PrayerType.ISHA])
                end_time = user_tz.localize(end_datetime)
            else:
                # Fallback: 1.5 hours after Maghrib
                end_time = start_time + timedelta(hours=1, minutes=30)
                
        elif prayer.prayer_type == PrayerType.ISHA:
            # Isha ends at next day's Fajr
            # For Isha, we need to set the end time to next day's Fajr (03:21)
            # Since Isha is typically at 19:21 and Fajr is at 05:21, we add 10 hours
            # But to be safe, let's add 8 hours and then add a day
            end_time = start_time + timedelta(hours=8, days=1)
        else:
            # Default fallback
            end_time = start_time + timedelta(hours=2)

        return start_time, end_time

    def _get_prayer_time_status(self, prayer: Prayer, user: User, date: datetime.date) -> str:
        """
        Get the prayer time status based on current time relative to prayer window.

        Args:
            prayer: Prayer instance.
            user: User instance.
            date: Date of the prayer.

        Returns:
            str: Time status ('future', 'pending', 'missed').
        """
        try:
            # Get user timezone
            user_tz = pytz.timezone(user.timezone)
            now = datetime.now(user_tz)

            # Get prayer time window
            start_time, end_time = self._get_prayer_time_window(prayer)

            # Determine status based on current time
            if now < start_time:
                return 'future'  # Before prayer start time
            elif now <= end_time:
                return 'pending'  # Between start and end time
            else:
                return 'missed'  # After prayer end time

        except Exception as e:
            self.logger.error(f"Error getting prayer time status: {str(e)}")
            return 'missed'

    def _can_mark_qada(self, prayer: Prayer, completion: Optional[PrayerCompletion],
                      time_status: str, user: User, date: datetime.date) -> bool:
        """
        Check if a prayer can be marked as Qada.

        Args:
            prayer: Prayer instance.
            completion: Prayer completion instance if exists.
            time_status: Time status ('future', 'pending', 'missed').
            user: User instance.
            date: Date of the prayer.

        Returns:
            bool: True if prayer can be marked as Qada, False otherwise.
        """
        # Can't mark Qada before account creation
        if date < user.created_at.date():
            return False

        # Can mark Qada if prayer is missed and not completed
        if time_status == 'missed' and not completion:
            return True

        # Can mark Qada if prayer is marked as missed
        if completion and completion.status == PrayerStatus.MISSED:
            return True

        return False

    def _auto_update_prayer_status(self, user: User, prayers: List[Prayer], date: datetime.date) -> None:
        """
        Automatically update prayer statuses for a list of prayers.

        Args:
            user: User instance.
            prayers: List of prayer instances.
            date: Date of the prayers.
        """
        for prayer in prayers:
            self._auto_update_single_prayer(prayer, user, date)

    def _auto_update_single_prayer(self, prayer: Prayer, user: User, date: datetime.date) -> bool:
        """
        Automatically update status for a single prayer.

        Args:
            prayer: Prayer instance.
            user: User instance.
            date: Date of the prayer.

        Returns:
            bool: True if prayer status was updated, False otherwise.
        """
        try:
            # Check if prayer is missed and not completed
            is_missed = self._is_prayer_missed(prayer, user, date)
            existing_completion = self._get_prayer_completion(prayer.id)

            if is_missed and not existing_completion:
                # Automatically mark as missed
                self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer.id,
                    user_id=user.id,
                    marked_at=None,  # No timestamp for missed prayers
                    status=PrayerStatus.MISSED
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error auto-updating prayer {prayer.id}: {str(e)}")
            return False

    def _is_prayer_missed(self, prayer: Prayer, user: User, date: datetime.date) -> bool:
        """
        Check if a prayer is missed based on current time.
        
        Args:
            prayer: Prayer instance.
            user: User instance.
            date: Date of the prayer.
            
        Returns:
            bool: True if prayer is missed, False otherwise.
        """
        try:
            # Get prayer time status
            time_status = self._get_prayer_time_status(prayer, user, date)
            return time_status == 'missed'
        except Exception as e:
            self.logger.error(f"Error checking if prayer is missed: {str(e)}")
            return False
