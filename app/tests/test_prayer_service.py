"""
Unit tests for the prayer service.

This module contains comprehensive unit tests for the PrayerService class,
testing prayer time management, completion tracking, and Qada functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, time, timedelta

from app.services.prayer_service import PrayerService
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.utils.exceptions import PrayerNotFoundError, PrayerTimeError


class TestPrayerService:
    """Test class for PrayerService."""
    
    def test_init(self, app):
        """Test PrayerService initialization."""
        with app.app_context():
            service = PrayerService()
            assert service is not None
            assert service.api_config is not None
            assert service.prayer_time_window is not None
    
    def test_get_prayer_times_success(self, db_session, sample_user, mock_prayer_times_api):
        """Test successful prayer times retrieval."""
        service = PrayerService()
        result = service.get_prayer_times(sample_user.id)
        
        assert result['success'] is True
        assert 'prayers' in result
        assert 'date' in result
        assert 'user_timezone' in result
    
    def test_get_prayer_times_user_not_found(self, db_session):
        """Test prayer times retrieval with non-existent user."""
        service = PrayerService()
        result = service.get_prayer_times(999)
        
        assert result['success'] is False
        assert 'User not found' in result['error']
    
    def test_get_prayer_times_invalid_date(self, db_session, sample_user):
        """Test prayer times retrieval with invalid date format."""
        service = PrayerService()
        result = service.get_prayer_times(sample_user.id, 'invalid-date')
        
        assert result['success'] is False
        assert 'Invalid date format' in result['error']
    
    def test_get_prayer_times_before_account_creation(self, db_session, sample_user):
        """Test prayer times retrieval before account creation."""
        # Set user creation date to today
        sample_user.created_at = datetime.now()
        db_session.commit()
        
        # Try to get prayer times for yesterday
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        service = PrayerService()
        result = service.get_prayer_times(sample_user.id, yesterday)
        
        assert result['success'] is False
        assert 'Cannot access prayer times before account creation' in result['error']
    
    def test_complete_prayer_success(self, db_session, sample_user, sample_prayer):
        """Test successful prayer completion."""
        with patch('app.services.prayer_service.PrayerService._validate_prayer_time', return_value=(True, False)):
            service = PrayerService()
            result = service.complete_prayer(sample_user.id, sample_prayer.id)
            
            assert result['success'] is True
            assert 'completion' in result
            assert 'Prayer completed successfully' in result['message']
    
    def test_complete_prayer_not_found(self, db_session, sample_user):
        """Test prayer completion with non-existent prayer."""
        service = PrayerService()
        result = service.complete_prayer(sample_user.id, 999)
        
        assert result['success'] is False
        assert 'Prayer not found' in result['error']
    
    def test_complete_prayer_user_not_found(self, db_session, sample_prayer):
        """Test prayer completion with non-existent user."""
        service = PrayerService()
        result = service.complete_prayer(999, sample_prayer.id)
        
        assert result['success'] is False
        assert 'User not found' in result['error']
    
    def test_complete_prayer_already_completed(self, db_session, sample_user, sample_prayer, sample_prayer_completion):
        """Test prayer completion when already completed."""
        with patch('app.services.prayer_service.PrayerService._get_prayer_completion', return_value=sample_prayer_completion):
            service = PrayerService()
            result = service.complete_prayer(sample_user.id, sample_prayer.id)
            
            assert result['success'] is False
            assert 'Prayer already completed' in result['error']
    
    def test_complete_prayer_time_not_valid(self, db_session, sample_user, sample_prayer):
        """Test prayer completion outside valid time window."""
        with patch('app.services.prayer_service.PrayerService._validate_prayer_time', return_value=(False, False)):
            service = PrayerService()
            result = service.complete_prayer(sample_user.id, sample_prayer.id)
            
            assert result['success'] is False
            assert 'Prayer time has not started yet' in result['error']
    
    def test_mark_prayer_qada_success(self, db_session, sample_user, sample_prayer):
        """Test successful Qada marking."""
        service = PrayerService()
        result = service.mark_prayer_qada(sample_user.id, sample_prayer.id)
        
        assert result['success'] is True
        assert 'completion' in result
        assert 'Prayer marked as Qada successfully' in result['message']
    
    def test_mark_prayer_qada_prayer_not_found(self, db_session, sample_user):
        """Test Qada marking with non-existent prayer."""
        service = PrayerService()
        result = service.mark_prayer_qada(sample_user.id, 999)
        
        assert result['success'] is False
        assert 'Prayer not found' in result['error']
    
    def test_mark_prayer_qada_user_not_found(self, db_session, sample_prayer):
        """Test Qada marking with non-existent user."""
        service = PrayerService()
        result = service.mark_prayer_qada(999, sample_prayer.id)
        
        assert result['success'] is False
        assert 'User not found' in result['error']
    
    def test_mark_prayer_qada_before_account_creation(self, db_session, sample_user, sample_prayer):
        """Test Qada marking before account creation."""
        # Set prayer date before user creation
        sample_prayer.prayer_date = sample_user.created_at.date() - timedelta(days=1)
        db_session.commit()
        
        service = PrayerService()
        result = service.mark_prayer_qada(sample_user.id, sample_prayer.id)
        
        assert result['success'] is False
        assert 'Cannot mark prayers as Qada before account creation' in result['error']
    
    def test_mark_prayer_qada_update_existing_completion(self, db_session, sample_user, sample_prayer, sample_prayer_completion):
        """Test Qada marking with existing completion."""
        # Set existing completion as late but not Qada
        sample_prayer_completion.is_late = True
        sample_prayer_completion.is_qada = False
        db_session.commit()
        
        with patch('app.services.prayer_service.PrayerService._get_prayer_completion', return_value=sample_prayer_completion):
            service = PrayerService()
            result = service.mark_prayer_qada(sample_user.id, sample_prayer.id)
            
            assert result['success'] is True
            assert sample_prayer_completion.is_qada is True
    
    def test_auto_update_prayer_status_success(self, db_session, sample_user):
        """Test successful automatic prayer status update."""
        with patch('app.services.prayer_service.PrayerService._get_prayers_for_date', return_value=[]):
            service = PrayerService()
            result = service.auto_update_prayer_status(sample_user.id)
            
            assert result['success'] is True
            assert 'updated_count' in result
    
    def test_auto_update_prayer_status_user_not_found(self, db_session):
        """Test automatic prayer status update with non-existent user."""
        service = PrayerService()
        result = service.auto_update_prayer_status(999)
        
        assert result['success'] is False
        assert 'User not found' in result['error']
    
    def test_fetch_prayer_times_from_api_success(self, db_session, sample_user, mock_prayer_times_api):
        """Test successful prayer times fetching from API."""
        service = PrayerService()
        result = service._fetch_prayer_times_from_api(sample_user, date.today())
        
        assert isinstance(result, dict)
        assert 'Fajr' in result
        assert 'Dhuhr' in result
        assert 'Asr' in result
        assert 'Maghrib' in result
        assert 'Isha' in result
    
    def test_fetch_prayer_times_from_api_no_location(self, db_session, sample_user):
        """Test prayer times fetching with no location data."""
        # Remove location data
        sample_user.location_lat = None
        sample_user.location_lng = None
        db_session.commit()
        
        service = PrayerService()
        result = service._fetch_prayer_times_from_api(sample_user, date.today())
        
        assert result == {}
    
    def test_validate_prayer_time_on_time(self, db_session, sample_user):
        """Test prayer time validation when on time."""
        prayer_time = time(12, 0)  # 12:00 PM
        prayer = Prayer(
            user_id=sample_user.id,
            name='Dhuhr',
            prayer_time=prayer_time,
            prayer_date=date.today()
        )
        
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be within prayer window
            mock_now = datetime.combine(date.today(), time(12, 15))  # 12:15 PM
            mock_datetime.now.return_value = mock_now
            mock_datetime.combine = datetime.combine
            
            service = PrayerService()
            can_complete, is_late = service._validate_prayer_time(prayer, sample_user)
            
            assert can_complete is True
            assert is_late is False
    
    def test_validate_prayer_time_late(self, db_session, sample_user):
        """Test prayer time validation when late."""
        prayer_time = time(12, 0)  # 12:00 PM
        prayer = Prayer(
            user_id=sample_user.id,
            name='Dhuhr',
            prayer_time=prayer_time,
            prayer_date=date.today()
        )
        
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be after prayer window
            mock_now = datetime.combine(date.today(), time(13, 0))  # 1:00 PM
            mock_datetime.now.return_value = mock_now
            mock_datetime.combine = datetime.combine
            
            service = PrayerService()
            can_complete, is_late = service._validate_prayer_time(prayer, sample_user)
            
            assert can_complete is True
            assert is_late is True
    
    def test_validate_prayer_time_too_early(self, db_session, sample_user):
        """Test prayer time validation when too early."""
        prayer_time = time(12, 0)  # 12:00 PM
        prayer = Prayer(
            user_id=sample_user.id,
            name='Dhuhr',
            prayer_time=prayer_time,
            prayer_date=date.today()
        )
        
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be before prayer time
            mock_now = datetime.combine(date.today(), time(11, 30))  # 11:30 AM
            mock_datetime.now.return_value = mock_now
            mock_datetime.combine = datetime.combine
            
            service = PrayerService()
            can_complete, is_late = service._validate_prayer_time(prayer, sample_user)
            
            assert can_complete is False
            assert is_late is False
    
    def test_is_prayer_missed_true(self, db_session, sample_user):
        """Test prayer missed detection when missed."""
        prayer_time = time(12, 0)  # 12:00 PM
        prayer = Prayer(
            user_id=sample_user.id,
            name='Dhuhr',
            prayer_time=prayer_time,
            prayer_date=date.today()
        )
        
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be after prayer window
            mock_now = datetime.combine(date.today(), time(13, 0))  # 1:00 PM
            mock_datetime.now.return_value = mock_now
            mock_datetime.combine = datetime.combine
            
            service = PrayerService()
            is_missed = service._is_prayer_missed(prayer, sample_user, date.today())
            
            assert is_missed is True
    
    def test_is_prayer_missed_false(self, db_session, sample_user):
        """Test prayer missed detection when not missed."""
        prayer_time = time(12, 0)  # 12:00 PM
        prayer = Prayer(
            user_id=sample_user.id,
            name='Dhuhr',
            prayer_time=prayer_time,
            prayer_date=date.today()
        )
        
        with patch('datetime.datetime') as mock_datetime:
            # Mock current time to be within prayer window
            mock_now = datetime.combine(date.today(), time(12, 15))  # 12:15 PM
            mock_datetime.now.return_value = mock_now
            mock_datetime.combine = datetime.combine
            
            service = PrayerService()
            is_missed = service._is_prayer_missed(prayer, sample_user, date.today())
            
            assert is_missed is False
    
    def test_can_mark_qada_missed_prayer(self, db_session, sample_user, sample_prayer):
        """Test Qada marking capability for missed prayer."""
        with patch('app.services.prayer_service.PrayerService._is_prayer_missed', return_value=True):
            with patch('app.services.prayer_service.PrayerService._get_prayer_completion', return_value=None):
                service = PrayerService()
                can_mark = service._can_mark_qada(sample_prayer, None, True, sample_user, date.today())
                
                assert can_mark is True
    
    def test_can_mark_qada_late_completion(self, db_session, sample_user, sample_prayer, sample_prayer_completion):
        """Test Qada marking capability for late completion."""
        sample_prayer_completion.is_late = True
        sample_prayer_completion.is_qada = False
        
        service = PrayerService()
        can_mark = service._can_mark_qada(sample_prayer, sample_prayer_completion, False, sample_user, date.today())
        
        assert can_mark is True
    
    def test_can_mark_qada_before_account_creation(self, db_session, sample_user, sample_prayer):
        """Test Qada marking capability before account creation."""
        # Set prayer date before user creation
        prayer_date = sample_user.created_at.date() - timedelta(days=1)
        
        service = PrayerService()
        can_mark = service._can_mark_qada(sample_prayer, None, True, sample_user, prayer_date)
        
        assert can_mark is False
    
    def test_build_prayer_info(self, db_session, sample_user, sample_prayer, sample_prayer_completion):
        """Test prayer info building."""
        with patch('app.services.prayer_service.PrayerService._is_prayer_missed', return_value=False):
            with patch('app.services.prayer_service.PrayerService._validate_prayer_time', return_value=(True, False)):
                with patch('app.services.prayer_service.PrayerService._can_mark_qada', return_value=False):
                    service = PrayerService()
                    prayer_info = service._build_prayer_info(sample_prayer, sample_prayer_completion, sample_user, date.today())
                    
                    assert 'id' in prayer_info
                    assert 'name' in prayer_info
                    assert 'time' in prayer_info
                    assert 'completed' in prayer_info
                    assert 'can_complete' in prayer_info
                    assert 'is_missed' in prayer_info
                    assert 'can_mark_qada' in prayer_info
                    assert 'completion' in prayer_info
