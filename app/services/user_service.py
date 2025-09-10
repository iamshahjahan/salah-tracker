"""
User service for managing user profiles and settings.

This service handles user profile management, location updates, and user statistics
with proper validation and data integrity.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests

from .base_service import BaseService
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.config.settings import Config


class UserService(BaseService):
    """
    Service for managing user profiles and settings.
    
    This service provides methods for updating user profiles, managing locations,
    and calculating user statistics with proper validation.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the user service.
        
        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        self.api_config = self.config.EXTERNAL_API_CONFIG
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: ID of the user.
            
        Returns:
            Dict[str, Any]: User profile data or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'User profile retrieved successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'get_user_profile')
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: ID of the user.
            profile_data: Dictionary containing profile data to update.
            
        Returns:
            Dict[str, Any]: Update result with success status or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Validate and update allowed fields
            allowed_fields = [
                'first_name', 'last_name', 'phone_number', 
                'location_lat', 'location_lng', 'timezone', 'notification_enabled'
            ]
            
            update_data = {}
            for field in allowed_fields:
                if field in profile_data:
                    update_data[field] = profile_data[field]
            
            if not update_data:
                return {
                    'success': False,
                    'error': 'No valid fields to update'
                }
            
            # Update user record
            self.update_record(user, **update_data)
            
            self.logger.info(f"User profile updated: {user.email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'Profile updated successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'update_user_profile')
    
    def update_user_location(self, user_id: int, latitude: float, longitude: float, 
                           timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Update user location with geocoding to get city information.
        
        Args:
            user_id: ID of the user.
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.
            timezone: Optional timezone. If not provided, will be detected.
            
        Returns:
            Dict[str, Any]: Location update result with success status or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Validate coordinates
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return {
                    'success': False,
                    'error': 'Invalid coordinates'
                }
            
            # Get city information from coordinates
            city_info = self._get_city_from_coordinates(latitude, longitude)
            
            # Update user location
            update_data = {
                'location_lat': latitude,
                'location_lng': longitude
            }
            
            if timezone:
                update_data['timezone'] = timezone
            elif city_info.get('timezone'):
                update_data['timezone'] = city_info['timezone']
            
            self.update_record(user, **update_data)
            
            self.logger.info(f"User location updated: {user.email} - {city_info.get('city', 'Unknown')}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'city_info': city_info,
                'message': 'Location updated successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'update_user_location')
    
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get user prayer statistics and completion rates.
        
        Args:
            user_id: ID of the user.
            
        Returns:
            Dict[str, Any]: User statistics or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Calculate statistics
            stats = self._calculate_user_statistics(user)
            
            return {
                'success': True,
                'statistics': stats,
                'message': 'Statistics retrieved successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'get_user_statistics')
    
    def get_user_prayer_history(self, user_id: int, start_date: Optional[str] = None, 
                               end_date: Optional[str] = None, limit: int = 30) -> Dict[str, Any]:
        """
        Get user prayer completion history.
        
        Args:
            user_id: ID of the user.
            start_date: Start date in YYYY-MM-DD format. If None, uses user creation date.
            end_date: End date in YYYY-MM-DD format. If None, uses today.
            limit: Maximum number of records to return.
            
        Returns:
            Dict[str, Any]: Prayer history data or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Parse dates
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid start date format. Use YYYY-MM-DD'
                    }
            else:
                start_dt = user.created_at.date()
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid end date format. Use YYYY-MM-DD'
                    }
            else:
                end_dt = datetime.now().date()
            
            # Get prayer history
            history = self._get_prayer_history(user, start_dt, end_dt, limit)
            
            return {
                'success': True,
                'history': history,
                'start_date': start_dt.strftime('%Y-%m-%d'),
                'end_date': end_dt.strftime('%Y-%m-%d'),
                'message': 'Prayer history retrieved successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'get_user_prayer_history')
    
    def _get_city_from_coordinates(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get city information from coordinates using geocoding API.
        
        Args:
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.
            
        Returns:
            Dict[str, Any]: City information including name, country, and timezone.
        """
        try:
            url = f"{self.api_config.geocoding_base_url}/reverse-geocode"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'localityLanguage': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'city': data.get('city', 'Unknown'),
                'country': data.get('countryName', 'Unknown'),
                'timezone': data.get('timezone', {}).get('name', 'UTC')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting city from coordinates: {str(e)}")
            return {
                'city': 'Unknown',
                'country': 'Unknown',
                'timezone': 'UTC'
            }
    
    def _calculate_user_statistics(self, user: User) -> Dict[str, Any]:
        """
        Calculate comprehensive user statistics.
        
        Args:
            user: User instance.
            
        Returns:
            Dict[str, Any]: Dictionary containing various user statistics.
        """
        try:
            # Get date range
            start_date = user.created_at.date()
            end_date = datetime.now().date()
            total_days = (end_date - start_date).days + 1
            
            # Get all prayers for the user
            prayers = Prayer.query.filter(
                Prayer.user_id == user.id,
                Prayer.prayer_date >= start_date,
                Prayer.prayer_date <= end_date
            ).all()
            
            # Get all completions
            prayer_ids = [prayer.id for prayer in prayers]
            completions = PrayerCompletion.query.filter(
                PrayerCompletion.prayer_id.in_(prayer_ids)
            ).all()
            
            # Calculate statistics
            total_prayers = len(prayers)
            completed_prayers = len(completions)
            qada_prayers = len([c for c in completions if c.is_qada])
            late_prayers = len([c for c in completions if c.is_late])
            
            # Calculate completion rate
            completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
            
            # Calculate daily completion rates
            daily_stats = self._calculate_daily_completion_stats(prayers, completions, start_date, end_date)
            
            # Calculate prayer-specific statistics
            prayer_stats = self._calculate_prayer_specific_stats(prayers, completions)
            
            return {
                'total_days': total_days,
                'total_prayers': total_prayers,
                'completed_prayers': completed_prayers,
                'qada_prayers': qada_prayers,
                'late_prayers': late_prayers,
                'completion_rate': round(completion_rate, 2),
                'daily_stats': daily_stats,
                'prayer_stats': prayer_stats,
                'account_created': user.created_at.isoformat(),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating user statistics: {str(e)}")
            return {}
    
    def _calculate_daily_completion_stats(self, prayers: List[Prayer], completions: List[PrayerCompletion],
                                        start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """
        Calculate daily completion statistics.
        
        Args:
            prayers: List of prayer instances.
            completions: List of prayer completion instances.
            start_date: Start date for calculation.
            end_date: End date for calculation.
            
        Returns:
            Dict[str, Any]: Daily completion statistics.
        """
        try:
            # Group prayers by date
            prayers_by_date = {}
            for prayer in prayers:
                date_str = prayer.prayer_date.strftime('%Y-%m-%d')
                if date_str not in prayers_by_date:
                    prayers_by_date[date_str] = []
                prayers_by_date[date_str].append(prayer)
            
            # Group completions by prayer_id
            completions_by_prayer = {c.prayer_id: c for c in completions}
            
            # Calculate daily stats
            daily_stats = {}
            for date_str, date_prayers in prayers_by_date.items():
                total_prayers = len(date_prayers)
                completed_prayers = sum(1 for p in date_prayers if p.id in completions_by_prayer)
                daily_completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
                
                daily_stats[date_str] = {
                    'total_prayers': total_prayers,
                    'completed_prayers': completed_prayers,
                    'completion_rate': round(daily_completion_rate, 2)
                }
            
            return daily_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating daily completion stats: {str(e)}")
            return {}
    
    def _calculate_prayer_specific_stats(self, prayers: List[Prayer], 
                                       completions: List[PrayerCompletion]) -> Dict[str, Any]:
        """
        Calculate prayer-specific completion statistics.
        
        Args:
            prayers: List of prayer instances.
            completions: List of prayer completion instances.
            
        Returns:
            Dict[str, Any]: Prayer-specific statistics.
        """
        try:
            # Group prayers by name
            prayers_by_name = {}
            for prayer in prayers:
                if prayer.name not in prayers_by_name:
                    prayers_by_name[prayer.name] = []
                prayers_by_name[prayer.name].append(prayer)
            
            # Group completions by prayer_id
            completions_by_prayer = {c.prayer_id: c for c in completions}
            
            # Calculate prayer-specific stats
            prayer_stats = {}
            for prayer_name, prayer_list in prayers_by_name.items():
                total_prayers = len(prayer_list)
                completed_prayers = sum(1 for p in prayer_list if p.id in completions_by_prayer)
                qada_prayers = sum(1 for p in prayer_list 
                                 if p.id in completions_by_prayer 
                                 and completions_by_prayer[p.id].is_qada)
                
                completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
                
                prayer_stats[prayer_name] = {
                    'total_prayers': total_prayers,
                    'completed_prayers': completed_prayers,
                    'qada_prayers': qada_prayers,
                    'completion_rate': round(completion_rate, 2)
                }
            
            return prayer_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating prayer-specific stats: {str(e)}")
            return {}
    
    def _get_prayer_history(self, user: User, start_date: datetime.date, 
                           end_date: datetime.date, limit: int) -> List[Dict[str, Any]]:
        """
        Get prayer completion history for a user.
        
        Args:
            user: User instance.
            start_date: Start date for history.
            end_date: End date for history.
            limit: Maximum number of records to return.
            
        Returns:
            List[Dict[str, Any]]: List of prayer history records.
        """
        try:
            # Get prayers with completions
            prayers = Prayer.query.filter(
                Prayer.user_id == user.id,
                Prayer.prayer_date >= start_date,
                Prayer.prayer_date <= end_date
            ).order_by(Prayer.prayer_date.desc(), Prayer.prayer_time).limit(limit).all()
            
            # Get completions
            prayer_ids = [prayer.id for prayer in prayers]
            completions = PrayerCompletion.query.filter(
                PrayerCompletion.prayer_id.in_(prayer_ids)
            ).all()
            
            # Group completions by prayer_id
            completions_by_prayer = {c.prayer_id: c for c in completions}
            
            # Build history
            history = []
            for prayer in prayers:
                completion = completions_by_prayer.get(prayer.id)
                history.append({
                    'id': prayer.id,
                    'name': prayer.name,
                    'date': prayer.prayer_date.strftime('%Y-%m-%d'),
                    'time': prayer.prayer_time.strftime('%H:%M'),
                    'completed': completion is not None,
                    'completion': completion.to_dict() if completion else None
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting prayer history: {str(e)}")
            return []
