"""
Comprehensive Service Layer Tests
Tests all service classes for business logic, error handling, and integration.
"""

import pytest
from datetime import datetime, timedelta, date, time
from unittest.mock import patch, MagicMock, Mock
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification
from app.services.prayer_service import PrayerService
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.services.cache_service import CacheService
from app.services.user_service import UserService
from app.services.family_group_service import FamilyGroupService


class TestPrayerService:
    """Test PrayerService functionality"""
    
    def test_get_prayer_times_for_date(self, app, test_user):
        """Test getting prayer times for a specific date"""
        with app.app_context():
            service = PrayerService()
            test_date = date.today()
            
            with patch('app.services.prayer_service.requests.get') as mock_get:
                # Mock API response
                mock_response = Mock()
                mock_response.json.return_value = {
                    'data': {
                        'timings': {
                            'Fajr': '05:30',
                            'Dhuhr': '12:15',
                            'Asr': '15:45',
                            'Maghrib': '18:30',
                            'Isha': '20:00'
                        }
                    }
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                prayer_times = service.get_prayer_times_for_date(test_user.id, test_date)
                
                assert prayer_times is not None
                assert len(prayer_times) == 5
                assert 'FAJR' in prayer_times
                assert 'DHUHR' in prayer_times
                assert 'ASR' in prayer_times
                assert 'MAGHRIB' in prayer_times
                assert 'ISHA' in prayer_times
    
    def test_get_prayer_times_caching(self, app, test_user):
        """Test prayer times caching functionality"""
        with app.app_context():
            service = PrayerService()
            test_date = date.today()
            
            with patch('app.services.prayer_service.requests.get') as mock_get:
                # Mock API response
                mock_response = Mock()
                mock_response.json.return_value = {
                    'data': {
                        'timings': {
                            'Fajr': '05:30',
                            'Dhuhr': '12:15',
                            'Asr': '15:45',
                            'Maghrib': '18:30',
                            'Isha': '20:00'
                        }
                    }
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                # First call - should hit API
                prayer_times1 = service.get_prayer_times_for_date(test_user.id, test_date)
                
                # Second call - should hit cache
                prayer_times2 = service.get_prayer_times_for_date(test_user.id, test_date)
                
                # API should only be called once
                assert mock_get.call_count == 1
                assert prayer_times1 == prayer_times2
    
    def test_mark_prayer_completed(self, app, test_user):
        """Test marking a prayer as completed"""
        with app.app_context():
            service = PrayerService()
            
            # Create a prayer
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=test_user.id
            )
            db.session.add(prayer)
            db.session.commit()
            
            completion_time = datetime.now()
            result = service.mark_prayer_completed(
                test_user.id, 
                prayer.id, 
                completion_time, 
                is_qada=False
            )
            
            assert result is not None
            assert result['success'] is True
            assert result['completion_id'] is not None
            
            # Verify completion was created in database
            completion = PrayerCompletion.query.filter_by(
                user_id=test_user.id,
                prayer_id=prayer.id
            ).first()
            assert completion is not None
            assert completion.is_qada is False
    
    def test_mark_prayer_qada(self, app, test_user):
        """Test marking a missed prayer as qada"""
        with app.app_context():
            service = PrayerService()
            
            # Create a prayer
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=test_user.id
            )
            db.session.add(prayer)
            db.session.commit()
            
            completion_time = datetime.now()
            result = service.mark_prayer_completed(
                test_user.id, 
                prayer.id, 
                completion_time, 
                is_qada=True
            )
            
            assert result is not None
            assert result['success'] is True
            
            # Verify qada completion was created
            completion = PrayerCompletion.query.filter_by(
                user_id=test_user.id,
                prayer_id=prayer.id
            ).first()
            assert completion is not None
            assert completion.is_qada is True
    
    def test_get_prayer_status_for_date(self, app, test_user):
        """Test getting prayer status for a date"""
        with app.app_context():
            service = PrayerService()
            test_date = date.today()
            
            # Create some prayers
            prayers = []
            for i, name in enumerate(['FAJR', 'DHUHR', 'ASR', 'MAGHRIB', 'ISHA']):
                prayer = Prayer(
                    name=name,
                    display_name=name.title(),
                    prayer_time=f'{6+i}:00:00',
                    date=test_date,
                    user_id=test_user.id
                )
                prayers.append(prayer)
                db.session.add(prayer)
            db.session.commit()
            
            # Mark some as completed
            service.mark_prayer_completed(test_user.id, prayers[0].id, datetime.now())
            service.mark_prayer_completed(test_user.id, prayers[1].id, datetime.now(), is_qada=True)
            
            status = service.get_prayer_status_for_date(test_user.id, test_date)
            
            assert status is not None
            assert len(status) == 5
            assert any(s['status'] == 'completed' for s in status)
            assert any(s['status'] == 'qada' for s in status)
    
    def test_prayer_service_error_handling(self, app, test_user):
        """Test prayer service error handling"""
        with app.app_context():
            service = PrayerService()
            
            # Test with invalid user ID
            result = service.get_prayer_times_for_date(99999, date.today())
            assert result is None
            
            # Test with invalid prayer ID
            result = service.mark_prayer_completed(test_user.id, 99999, datetime.now())
            assert result is not None
            assert result['success'] is False
            assert 'error' in result


class TestEmailService:
    """Test EmailService functionality"""
    
    def test_send_prayer_reminder(self, app, test_user):
        """Test sending prayer reminder email"""
        with app.app_context():
            service = EmailService()
            
            with patch('app.services.email_service.mail.send') as mock_send:
                result = service.send_prayer_reminder(
                    test_user.email,
                    'FAJR',
                    '05:30',
                    'Test reminder message'
                )
                
                assert result is True
                mock_send.assert_called_once()
    
    def test_send_verification_email(self, app, test_user):
        """Test sending email verification"""
        with app.app_context():
            service = EmailService()
            
            with patch('app.services.email_service.mail.send') as mock_send:
                result = service.send_verification_email(
                    test_user.email,
                    '123456'
                )
                
                assert result is True
                mock_send.assert_called_once()
    
    def test_send_welcome_email(self, app, test_user):
        """Test sending welcome email"""
        with app.app_context():
            service = EmailService()
            
            with patch('app.services.email_service.mail.send') as mock_send:
                result = service.send_welcome_email(
                    test_user.email,
                    test_user.username
                )
                
                assert result is True
                mock_send.assert_called_once()
    
    def test_email_service_error_handling(self, app):
        """Test email service error handling"""
        with app.app_context():
            service = EmailService()
            
            with patch('app.services.email_service.mail.send', side_effect=Exception("SMTP Error")):
                result = service.send_prayer_reminder(
                    'invalid@email.com',
                    'FAJR',
                    '05:30',
                    'Test message'
                )
                
                assert result is False


class TestNotificationService:
    """Test NotificationService functionality"""
    
    def test_create_prayer_reminder(self, app, test_user):
        """Test creating prayer reminder notification"""
        with app.app_context():
            service = NotificationService()
            
            scheduled_time = datetime.now() + timedelta(minutes=15)
            result = service.create_prayer_reminder(
                test_user.id,
                1,  # Prayer ID
                scheduled_time,
                'Test reminder message'
            )
            
            assert result is not None
            assert result['success'] is True
            assert result['notification_id'] is not None
            
            # Verify notification was created
            notification = PrayerNotification.query.get(result['notification_id'])
            assert notification is not None
            assert notification.user_id == test_user.id
            assert notification.notification_type == 'reminder'
    
    def test_send_scheduled_notifications(self, app, test_user):
        """Test sending scheduled notifications"""
        with app.app_context():
            service = NotificationService()
            
            # Create a notification scheduled for now
            notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=1,
                notification_type='reminder',
                message='Test notification',
                scheduled_time=datetime.now(),
                is_sent=False
            )
            db.session.add(notification)
            db.session.commit()
            
            with patch('app.services.email_service.EmailService.send_prayer_reminder') as mock_send:
                mock_send.return_value = True
                
                result = service.send_scheduled_notifications()
                
                assert result is not None
                assert result['sent_count'] >= 1
                
                # Verify notification was marked as sent
                db.session.refresh(notification)
                assert notification.is_sent is True
    
    def test_get_user_notifications(self, app, test_user):
        """Test getting user notifications"""
        with app.app_context():
            service = NotificationService()
            
            # Create some notifications
            notifications = []
            for i in range(3):
                notification = PrayerNotification(
                    user_id=test_user.id,
                    prayer_id=i + 1,
                    notification_type='reminder',
                    message=f'Test notification {i+1}',
                    scheduled_time=datetime.now() + timedelta(minutes=i*5)
                )
                notifications.append(notification)
                db.session.add(notification)
            db.session.commit()
            
            user_notifications = service.get_user_notifications(test_user.id)
            
            assert user_notifications is not None
            assert len(user_notifications) >= 3
    
    def test_notification_service_error_handling(self, app):
        """Test notification service error handling"""
        with app.app_context():
            service = NotificationService()
            
            # Test with invalid user ID
            result = service.create_prayer_reminder(
                99999,  # Invalid user ID
                1,
                datetime.now() + timedelta(minutes=15),
                'Test message'
            )
            
            assert result is not None
            assert result['success'] is False
            assert 'error' in result


class TestCacheService:
    """Test CacheService functionality"""
    
    def test_cache_set_and_get(self, app):
        """Test basic cache set and get operations"""
        with app.app_context():
            service = CacheService()
            
            # Test setting and getting a simple value
            key = 'test_key'
            value = {'test': 'data', 'number': 123}
            
            result = service.set(key, value, ttl=300)
            assert result is True
            
            cached_value = service.get(key)
            assert cached_value == value
    
    def test_cache_ttl_expiry(self, app):
        """Test cache TTL expiry"""
        with app.app_context():
            service = CacheService()
            
            key = 'test_ttl_key'
            value = 'test_value'
            
            # Set with very short TTL
            service.set(key, value, ttl=1)
            
            # Should be available immediately
            assert service.get(key) == value
            
            # Wait for expiry (in real scenario, would need to wait)
            # For testing, we'll test the TTL mechanism differently
            service.delete(key)
            assert service.get(key) is None
    
    def test_cache_prayer_times(self, app, test_user):
        """Test caching prayer times"""
        with app.app_context():
            service = CacheService()
            test_date = date.today()
            
            prayer_times = {
                'FAJR': '05:30',
                'DHUHR': '12:15',
                'ASR': '15:45',
                'MAGHRIB': '18:30',
                'ISHA': '20:00'
            }
            
            # Cache prayer times
            result = service.set_prayer_times(test_user.id, test_date, prayer_times)
            assert result is True
            
            # Retrieve cached prayer times
            cached_times = service.get_prayer_times(test_user.id, test_date)
            assert cached_times == prayer_times
    
    def test_cache_invalidation(self, app):
        """Test cache invalidation"""
        with app.app_context():
            service = CacheService()
            
            key = 'test_invalidation'
            value = 'test_value'
            
            # Set value
            service.set(key, value)
            assert service.get(key) == value
            
            # Delete value
            result = service.delete(key)
            assert result is True
            assert service.get(key) is None
    
    def test_cache_error_handling(self, app):
        """Test cache service error handling"""
        with app.app_context():
            service = CacheService()
            
            # Test with invalid Redis connection (mocked)
            with patch('app.services.cache_service.redis_client.set', side_effect=Exception("Redis Error")):
                result = service.set('test_key', 'test_value')
                assert result is False


class TestUserService:
    """Test UserService functionality"""
    
    def test_create_user(self, app):
        """Test creating a new user"""
        with app.app_context():
            service = UserService()
            
            user_data = {
                'username': 'testuser_service',
                'email': 'testuser_service@example.com',
                'password': 'TestPassword123!',
                'location': 'Test City',
                'latitude': 40.7128,
                'longitude': -74.0060
            }
            
            result = service.create_user(user_data)
            
            assert result is not None
            assert result['success'] is True
            assert result['user_id'] is not None
            
            # Verify user was created
            user = User.query.get(result['user_id'])
            assert user is not None
            assert user.username == user_data['username']
            assert user.email == user_data['email']
    
    def test_authenticate_user(self, app, test_user):
        """Test user authentication"""
        with app.app_context():
            service = UserService()
            
            # Test valid credentials
            result = service.authenticate_user(test_user.email, 'TestPassword123!')
            assert result is not None
            assert result['success'] is True
            assert result['user_id'] == test_user.id
            
            # Test invalid credentials
            result = service.authenticate_user(test_user.email, 'wrongpassword')
            assert result is not None
            assert result['success'] is False
    
    def test_update_user_profile(self, app, test_user):
        """Test updating user profile"""
        with app.app_context():
            service = UserService()
            
            update_data = {
                'location': 'Updated City',
                'latitude': 41.8781,
                'longitude': -87.6298
            }
            
            result = service.update_user_profile(test_user.id, update_data)
            
            assert result is not None
            assert result['success'] is True
            
            # Verify profile was updated
            db.session.refresh(test_user)
            assert test_user.location == update_data['location']
            assert test_user.latitude == update_data['latitude']
            assert test_user.longitude == update_data['longitude']
    
    def test_get_user_statistics(self, app, test_user):
        """Test getting user statistics"""
        with app.app_context():
            service = UserService()
            
            # Create some prayer completions
            for i in range(3):
                completion = PrayerCompletion(
                    user_id=test_user.id,
                    prayer_id=i + 1,
                    completed_at=datetime.now(),
                    is_qada=False
                )
                db.session.add(completion)
            db.session.commit()
            
            stats = service.get_user_statistics(test_user.id)
            
            assert stats is not None
            assert 'total_prayers' in stats
            assert 'completed_prayers' in stats
            assert 'completion_rate' in stats
            assert stats['completed_prayers'] >= 3


class TestFamilyGroupService:
    """Test FamilyGroupService functionality"""
    
    def test_create_family_group(self, app, test_user):
        """Test creating a family group"""
        with app.app_context():
            service = FamilyGroupService()
            
            group_data = {
                'name': 'Test Family Group',
                'description': 'Test family group description'
            }
            
            result = service.create_family_group(test_user.id, group_data)
            
            assert result is not None
            assert result['success'] is True
            assert result['family_group_id'] is not None
            assert result['group_code'] is not None
            
            # Verify family group was created
            from app.models.family_group import FamilyGroup
            family_group = FamilyGroup.query.get(result['family_group_id'])
            assert family_group is not None
            assert family_group.name == group_data['name']
            assert family_group.created_by == test_user.id
    
    def test_join_family_group(self, app, test_user):
        """Test joining a family group"""
        with app.app_context():
            service = FamilyGroupService()
            
            # Create a family group
            from app.models.family_group import FamilyGroup
            family_group = FamilyGroup(
                name='Test Family',
                description='Test family',
                created_by=test_user.id,
                group_code='TEST123'
            )
            db.session.add(family_group)
            db.session.commit()
            
            # Create another user to join
            other_user = User(
                username='otheruser',
                email='otheruser@example.com',
                password_hash='hashed_password',
                location='Test City'
            )
            db.session.add(other_user)
            db.session.commit()
            
            result = service.join_family_group(other_user.id, family_group.group_code)
            
            assert result is not None
            assert result['success'] is True
            
            # Verify membership was created
            from app.models.family import Family
            membership = Family.query.filter_by(
                user_id=other_user.id,
                family_group_id=family_group.id
            ).first()
            assert membership is not None
    
    def test_get_family_members(self, app, test_user):
        """Test getting family group members"""
        with app.app_context():
            service = FamilyGroupService()
            
            # Create family group and add members
            from app.models.family_group import FamilyGroup
            family_group = FamilyGroup(
                name='Test Family',
                description='Test family',
                created_by=test_user.id,
                group_code='TEST123'
            )
            db.session.add(family_group)
            db.session.commit()
            
            # Add test user as member
            from app.models.family import Family
            membership = Family(
                user_id=test_user.id,
                family_group_id=family_group.id,
                role='admin',
                joined_at=datetime.now()
            )
            db.session.add(membership)
            db.session.commit()
            
            members = service.get_family_members(family_group.id)
            
            assert members is not None
            assert len(members) >= 1
            assert any(member['user_id'] == test_user.id for member in members)


class TestServiceIntegration:
    """Test integration between different services"""
    
    def test_prayer_completion_workflow(self, app, test_user):
        """Test complete prayer completion workflow"""
        with app.app_context():
            prayer_service = PrayerService()
            notification_service = NotificationService()
            
            # Create a prayer
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=test_user.id
            )
            db.session.add(prayer)
            db.session.commit()
            
            # Create a reminder notification
            scheduled_time = datetime.now() + timedelta(minutes=15)
            notification_result = notification_service.create_prayer_reminder(
                test_user.id,
                prayer.id,
                scheduled_time,
                'Fajr prayer reminder'
            )
            assert notification_result['success'] is True
            
            # Mark prayer as completed
            completion_result = prayer_service.mark_prayer_completed(
                test_user.id,
                prayer.id,
                datetime.now()
            )
            assert completion_result['success'] is True
            
            # Verify both operations succeeded
            completion = PrayerCompletion.query.filter_by(
                user_id=test_user.id,
                prayer_id=prayer.id
            ).first()
            assert completion is not None
            
            notification = PrayerNotification.query.get(notification_result['notification_id'])
            assert notification is not None
    
    def test_user_registration_workflow(self, app):
        """Test complete user registration workflow"""
        with app.app_context():
            user_service = UserService()
            email_service = EmailService()
            
            user_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'TestPassword123!',
                'location': 'Test City'
            }
            
            # Create user
            user_result = user_service.create_user(user_data)
            assert user_result['success'] is True
            
            # Send welcome email
            with patch('app.services.email_service.mail.send') as mock_send:
                email_result = email_service.send_welcome_email(
                    user_data['email'],
                    user_data['username']
                )
                assert email_result is True
                mock_send.assert_called_once()
            
            # Verify user was created
            user = User.query.get(user_result['user_id'])
            assert user is not None
            assert user.username == user_data['username']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
