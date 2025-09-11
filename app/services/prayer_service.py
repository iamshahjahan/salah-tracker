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

from .base_service import BaseService
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
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
        self.api_config = self.config.EXTERNAL_API_CONFIG
        self.prayer_time_window = self.config.PRAYER_TIME_WINDOW_MINUTES

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
            # Get user
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
                target_date = datetime.now().date()

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

            return {
                'success': True,
                'prayers': prayer_data,
                'date': target_date.strftime('%Y-%m-%d'),
                'user_timezone': user.timezone
            }

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

            # Create completion record
            completion = self.create_record(
                PrayerCompletion,
                prayer_id=prayer_id,
                user_id=user_id,
                completed_at=datetime.utcnow(),
                is_late=is_late,
                is_qada=False
            )

            self.logger.info(f"Prayer completed: {prayer.name} for user {user.email}")

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
                # Update existing completion to Qada
                self.update_record(
                    existing_completion,
                    is_qada=True,
                    is_late=True
                )
                completion = existing_completion
            else:
                # Create new Qada completion
                completion = self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer_id,
                    user_id=user_id,
                    completed_at=datetime.utcnow(),
                    is_late=True,
                    is_qada=True
                )

            self.logger.info(f"Prayer marked as Qada: {prayer.name} for user {user.email}")

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
            return []

        # Create prayer records
        prayers = []
        for prayer_name, prayer_time in prayer_times.items():
            prayer = self.create_record(
                Prayer,
                user_id=user.id,
                name=prayer_name,
                prayer_time=prayer_time,
                prayer_date=date
            )
            prayers.append(prayer)

        return prayers

    def _fetch_prayer_times_from_api(self, user: User, date: datetime.date) -> Dict[str, datetime.time]:
        """
        Fetch prayer times from external API.

        Args:
            user: User instance with location data.
            date: Date to fetch prayer times for.

        Returns:
            Dict[str, datetime.time]: Dictionary mapping prayer names to times.
        """
        try:
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
        # Check if prayer is missed
        is_missed = self._is_prayer_missed(prayer, user, date)

        # Check if prayer time is valid for completion
        can_complete, is_late = self._validate_prayer_time(prayer, user)

        # Determine if can mark as Qada
        can_mark_qada = self._can_mark_qada(prayer, completion, is_missed, user, date)

        prayer_info = {
            'id': prayer.id,
            'name': prayer.name,
            'time': prayer.prayer_time.strftime('%H:%M'),
            'completed': completion is not None,
            'can_complete': can_complete,
            'is_missed': is_missed,
            'can_mark_qada': can_mark_qada,
            'completion': completion.to_dict() if completion else None
        }

        return prayer_info

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
            prayer_datetime = user_tz.localize(
                datetime.combine(prayer.prayer_date, prayer.prayer_time)
            )

            # Calculate prayer time window
            window_start = prayer_datetime
            window_end = prayer_datetime + timedelta(minutes=self.prayer_time_window)

            # Check if current time is within prayer window
            if now < window_start:
                return False, False  # Too early
            elif now <= window_end:
                return True, False   # On time
            else:
                return True, True    # Late but can still complete

        except Exception as e:
            self.logger.error(f"Error validating prayer time: {str(e)}")
            return False, False

    def _is_prayer_missed(self, prayer: Prayer, user: User, date: datetime.date) -> bool:
        """
        Check if a prayer is missed (time has passed without completion).

        Args:
            prayer: Prayer instance.
            user: User instance.
            date: Date of the prayer.

        Returns:
            bool: True if prayer is missed, False otherwise.
        """
        try:
            # Get user timezone
            user_tz = pytz.timezone(user.timezone)
            now = datetime.now(user_tz)

            # Get prayer time in user timezone
            prayer_datetime = user_tz.localize(
                datetime.combine(prayer.prayer_date, prayer.prayer_time)
            )

            # Calculate prayer time window end
            window_end = prayer_datetime + timedelta(minutes=self.prayer_time_window)

            # Check if prayer time has passed
            return now > window_end

        except Exception as e:
            self.logger.error(f"Error checking if prayer is missed: {str(e)}")
            return False

    def _can_mark_qada(self, prayer: Prayer, completion: Optional[PrayerCompletion],
                      is_missed: bool, user: User, date: datetime.date) -> bool:
        """
        Check if a prayer can be marked as Qada.

        Args:
            prayer: Prayer instance.
            completion: Prayer completion instance if exists.
            is_missed: Whether the prayer is missed.
            user: User instance.
            date: Date of the prayer.

        Returns:
            bool: True if prayer can be marked as Qada, False otherwise.
        """
        # Can't mark Qada before account creation
        if date < user.created_at.date():
            return False

        # Can mark Qada if prayer is missed and not completed
        if is_missed and not completion:
            return True

        # Can mark Qada if prayer is completed late but not already marked as Qada
        if completion and completion.is_late and not completion.is_qada:
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
                # Automatically mark as not completed (missed)
                self.create_record(
                    PrayerCompletion,
                    prayer_id=prayer.id,
                    user_id=user.id,
                    completed_at=datetime.utcnow(),
                    is_late=True,
                    is_qada=False
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error auto-updating prayer {prayer.id}: {str(e)}")
            return False
