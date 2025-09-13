"""
Test cases for caching functionality.

This module tests the cache service, prayer service caching, and dashboard caching.
"""

import unittest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
import json

from app.services.cache_service import CacheService, cache_service
from app.services.prayer_service import PrayerService
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerStatus, PrayerType


class TestCacheService(unittest.TestCase):
    """Test cases for the CacheService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache_service = CacheService()

    def test_get_set_delete(self):
        """Test basic cache operations."""
        key = "test_key"
        value = {"test": "data", "number": 123}
        
        # Test set and get
        self.assertTrue(self.cache_service.set(key, value, 60))
        cached_value = self.cache_service.get(key)
        self.assertEqual(cached_value, value)
        
        # Test delete
        self.assertTrue(self.cache_service.delete(key))
        self.assertIsNone(self.cache_service.get(key))

    def test_ttl_expiration(self):
        """Test that cached values expire after TTL."""
        key = "expire_test"
        value = {"expire": "test"}
        
        # Set with 1 second TTL
        self.cache_service.set(key, value, 1)
        self.assertEqual(self.cache_service.get(key), value)
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertIsNone(self.cache_service.get(key))

    def test_prayer_times_caching(self):
        """Test prayer times specific caching methods."""
        user_id = 123
        date_str = "2025-09-13"
        prayer_data = {
            "success": True,
            "prayers": [
                {"prayer_type": "FAJR", "prayer_time": "05:10", "status": "completed"}
            ],
            "date": date_str
        }
        
        # Test set and get
        self.assertTrue(self.cache_service.set_prayer_times(user_id, date_str, prayer_data, 60))
        cached_data = self.cache_service.get_prayer_times(user_id, date_str)
        self.assertEqual(cached_data, prayer_data)
        
        # Test invalidation
        self.assertTrue(self.cache_service.invalidate_prayer_times(user_id, date_str))
        self.assertIsNone(self.cache_service.get_prayer_times(user_id, date_str))

    def test_dashboard_stats_caching(self):
        """Test dashboard stats specific caching methods."""
        user_id = 123
        stats_data = {
            "overall": {"total_prayers": 100, "completed_prayers": 80},
            "current_streak": 5
        }
        
        # Test set and get
        self.assertTrue(self.cache_service.set_dashboard_stats(user_id, stats_data, 60))
        cached_data = self.cache_service.get_dashboard_stats(user_id)
        self.assertEqual(cached_data, stats_data)
        
        # Test invalidation
        self.assertTrue(self.cache_service.invalidate_dashboard_stats(user_id))
        self.assertIsNone(self.cache_service.get_dashboard_stats(user_id))

    def test_weekly_calendar_caching(self):
        """Test weekly calendar specific caching methods."""
        user_id = 123
        week_start = "2025-09-08"
        calendar_data = {
            "week_start": week_start,
            "days": [
                {"date": "2025-09-08", "status": "completed"},
                {"date": "2025-09-09", "status": "pending"}
            ]
        }
        
        # Test set and get
        self.assertTrue(self.cache_service.set_weekly_calendar(user_id, week_start, calendar_data, 60))
        cached_data = self.cache_service.get_weekly_calendar(user_id, week_start)
        self.assertEqual(cached_data, calendar_data)
        
        # Test invalidation
        self.assertTrue(self.cache_service.invalidate_weekly_calendar(user_id, week_start))
        self.assertIsNone(self.cache_service.get_weekly_calendar(user_id, week_start))

    def test_pattern_deletion(self):
        """Test pattern-based cache deletion."""
        user_id = 123
        
        # Set multiple prayer times
        self.cache_service.set_prayer_times(user_id, "2025-09-13", {"data": "day1"}, 60)
        self.cache_service.set_prayer_times(user_id, "2025-09-14", {"data": "day2"}, 60)
        self.cache_service.set_dashboard_stats(user_id, {"stats": "data"}, 60)
        
        # Test user-specific invalidation
        deleted_count = self.cache_service.invalidate_user_prayer_times(user_id)
        self.assertGreaterEqual(deleted_count, 2)
        
        # Verify prayer times are deleted but dashboard stats remain
        self.assertIsNone(self.cache_service.get_prayer_times(user_id, "2025-09-13"))
        self.assertIsNone(self.cache_service.get_prayer_times(user_id, "2025-09-14"))
        self.assertIsNotNone(self.cache_service.get_dashboard_stats(user_id))


class TestPrayerServiceCaching(unittest.TestCase):
    """Test cases for PrayerService caching integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.prayer_service = PrayerService()

    @patch('app.services.prayer_service.cache_service')
    @patch('app.services.prayer_service.PrayerService._get_or_create_prayers')
    @patch('app.services.prayer_service.PrayerService._auto_update_prayer_status')
    @patch('app.services.prayer_service.PrayerService._build_prayer_info')
    @patch('app.services.prayer_service.PrayerService.get_record_by_id')
    def test_get_prayer_times_cache_hit(self, mock_get_user, mock_build_info, 
                                       mock_auto_update, mock_get_prayers, mock_cache):
        """Test that get_prayer_times returns cached data when available."""
        user_id = 123
        date_str = "2025-09-13"
        cached_data = {
            "success": True,
            "prayers": [{"prayer_type": "FAJR", "status": "completed"}],
            "date": date_str
        }
        
        # Mock cache hit
        mock_cache.get_prayer_times.return_value = cached_data
        
        result = self.prayer_service.get_prayer_times(user_id, date_str)
        
        # Verify cache was checked
        mock_cache.get_prayer_times.assert_called_once_with(user_id, date_str)
        
        # Verify database methods were not called
        mock_get_user.assert_not_called()
        mock_get_prayers.assert_not_called()
        
        # Verify cached result is returned
        self.assertEqual(result, cached_data)

    @patch('app.services.prayer_service.cache_service')
    @patch('app.services.prayer_service.PrayerService._get_or_create_prayers')
    @patch('app.services.prayer_service.PrayerService._auto_update_prayer_status')
    @patch('app.services.prayer_service.PrayerService._build_prayer_info')
    @patch('app.services.prayer_service.PrayerService.get_record_by_id')
    def test_get_prayer_times_cache_miss(self, mock_get_user, mock_build_info,
                                        mock_auto_update, mock_get_prayers, mock_cache):
        """Test that get_prayer_times fetches from database and caches result on cache miss."""
        user_id = 123
        date_str = "2025-09-13"
        
        # Mock cache miss
        mock_cache.get_prayer_times.return_value = None
        
        # Mock user and prayers
        mock_user = MagicMock()
        mock_user.created_at.date.return_value = date(2025, 1, 1)
        mock_user.timezone = "UTC"
        mock_get_user.return_value = mock_user
        
        mock_prayer = MagicMock()
        mock_prayer.id = 1
        mock_get_prayers.return_value = [mock_prayer]
        
        mock_build_info.return_value = {"prayer_type": "FAJR", "status": "completed"}
        
        result = self.prayer_service.get_prayer_times(user_id, date_str)
        
        # Verify cache was checked
        mock_cache.get_prayer_times.assert_called_once_with(user_id, date_str)
        
        # Verify database methods were called
        mock_get_user.assert_called_once_with(User, user_id)
        mock_get_prayers.assert_called_once()
        
        # Verify result was cached
        mock_cache.set_prayer_times.assert_called_once()
        
        # Verify result structure
        self.assertTrue(result['success'])
        self.assertEqual(result['date'], date_str)

    @patch('app.services.prayer_service.cache_service')
    @patch('app.services.prayer_service.PrayerService.get_record_by_id')
    @patch('app.services.prayer_service.PrayerService._get_prayer_completion')
    @patch('app.services.prayer_service.PrayerService._validate_prayer_time')
    @patch('app.services.prayer_service.PrayerService.create_record')
    def test_complete_prayer_cache_invalidation(self, mock_create, mock_validate,
                                               mock_get_completion, mock_get_user, mock_cache):
        """Test that complete_prayer invalidates relevant caches."""
        user_id = 123
        prayer_id = 456
        
        # Mock prayer and user
        mock_prayer = MagicMock()
        mock_prayer.prayer_type.value = "FAJR"
        mock_prayer.prayer_date = date(2025, 9, 13)
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        
        mock_get_user.side_effect = [mock_prayer, mock_user]
        mock_get_completion.return_value = None
        mock_validate.return_value = (True, False)  # Valid, not late
        
        mock_completion = MagicMock()
        mock_completion.to_dict.return_value = {"id": 1, "status": "COMPLETE"}
        mock_create.return_value = mock_completion
        
        result = self.prayer_service.complete_prayer(user_id, prayer_id)
        
        # Verify cache invalidation calls
        mock_cache.invalidate_prayer_times.assert_called_once_with(user_id, "2025-09-13")
        mock_cache.invalidate_dashboard_stats.assert_called_once_with(user_id)
        mock_cache.invalidate_user_calendar.assert_called_once_with(user_id)
        
        # Verify success
        self.assertTrue(result['success'])

    @patch('app.services.prayer_service.cache_service')
    @patch('app.services.prayer_service.PrayerService.get_record_by_id')
    @patch('app.services.prayer_service.PrayerService._get_prayer_completion')
    @patch('app.services.prayer_service.PrayerService.create_record')
    def test_mark_prayer_qada_cache_invalidation(self, mock_create, mock_get_completion,
                                                mock_get_user, mock_cache):
        """Test that mark_prayer_qada invalidates relevant caches."""
        user_id = 123
        prayer_id = 456
        
        # Mock prayer and user
        mock_prayer = MagicMock()
        mock_prayer.prayer_type.value = "FAJR"
        mock_prayer.prayer_date = date(2025, 9, 13)
        mock_prayer.created_at.date.return_value = date(2025, 1, 1)
        
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.created_at.date.return_value = date(2025, 1, 1)
        
        mock_get_user.side_effect = [mock_prayer, mock_user]
        mock_get_completion.return_value = None  # No existing completion
        
        mock_completion = MagicMock()
        mock_completion.to_dict.return_value = {"id": 1, "status": "QADA"}
        mock_create.return_value = mock_completion
        
        result = self.prayer_service.mark_prayer_qada(user_id, prayer_id)
        
        # Verify cache invalidation calls
        mock_cache.invalidate_prayer_times.assert_called_once_with(user_id, "2025-09-13")
        mock_cache.invalidate_dashboard_stats.assert_called_once_with(user_id)
        mock_cache.invalidate_user_calendar.assert_called_once_with(user_id)
        
        # Verify success
        self.assertTrue(result['success'])


class TestDashboardCaching(unittest.TestCase):
    """Test cases for dashboard caching integration."""

    def setUp(self):
        """Set up Flask app context for testing."""
        from main import app
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up Flask app context."""
        self.app_context.pop()

    @patch('app.routes.dashboard.cache_service')
    @patch('app.routes.dashboard.User')
    @patch('app.routes.dashboard.db')
    def test_dashboard_stats_cache_hit(self, mock_db, mock_user_class, mock_cache):
        """Test that dashboard stats returns cached data when available."""
        from app.routes.dashboard import get_user_stats
        
        user_id = 123
        cached_data = {
            "overall": {"total_prayers": 100, "completed_prayers": 80},
            "current_streak": 5
        }
        
        # Mock cache hit
        mock_cache.get_dashboard_stats.return_value = cached_data
        
        # Mock Flask request context
        with patch('app.routes.dashboard.get_jwt_identity', return_value=user_id):
            with patch('app.routes.dashboard.jsonify') as mock_jsonify:
                get_user_stats()
                
                # Verify cache was checked
                mock_cache.get_dashboard_stats.assert_called_once_with(user_id)
                
                # Verify database was not queried
                mock_db.session.query.assert_not_called()
                
                # Verify cached result was returned
                mock_jsonify.assert_called_once_with(cached_data)

    @patch('app.routes.dashboard.cache_service')
    @patch('app.routes.dashboard.User')
    @patch('app.routes.dashboard.db')
    @patch('app.routes.dashboard.get_prayer_streak')
    def test_dashboard_stats_cache_miss(self, mock_streak, mock_db, mock_user_class, mock_cache):
        """Test that dashboard stats fetches from database and caches result on cache miss."""
        from app.routes.dashboard import get_user_stats
        
        user_id = 123
        
        # Mock cache miss
        mock_cache.get_dashboard_stats.return_value = None
        
        # Mock user
        mock_user = MagicMock()
        mock_user.created_at.date.return_value = date(2025, 1, 1)
        mock_user_class.query.get.return_value = mock_user
        
        # Mock database queries
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 100  # total_prayers
        mock_query.join.return_value.filter.return_value.count.return_value = 80  # completed_prayers
        mock_query.outerjoin.return_value.filter.return_value.group_by.return_value.all.return_value = []
        mock_db.session.query.return_value = mock_query
        
        mock_streak.return_value = 5
        
        # Mock Flask request context
        with patch('app.routes.dashboard.get_jwt_identity', return_value=user_id):
            with patch('app.routes.dashboard.jsonify') as mock_jsonify:
                get_user_stats()
                
                # Verify cache was checked
                mock_cache.get_dashboard_stats.assert_called_once_with(user_id)
                
                # Verify database was queried
                mock_db.session.query.assert_called()
                
                # Verify result was cached
                mock_cache.set_dashboard_stats.assert_called_once()
                
                # Verify result was returned
                mock_jsonify.assert_called_once()


if __name__ == '__main__':
    unittest.main()
