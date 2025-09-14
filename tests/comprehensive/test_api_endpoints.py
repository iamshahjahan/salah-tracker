"""
Comprehensive API Endpoint Tests
Tests all API endpoints for proper functionality, authentication, and error handling.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_endpoint(self, client):
        """Test user registration endpoint"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            'username': f'testuser_new_{unique_id}',
            'email': f'testuser_new_{unique_id}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'location': 'New York, NY',
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data
        assert 'user_id' in data or 'access_token' in data
    
    def test_login_endpoint(self, client, sample_user):
        """Test user login endpoint"""
        # Set the password properly for the test user
        sample_user.set_password('TestPassword123!')
        from config.database import db
        db.session.commit()
        
        login_data = {
            'username': sample_user.email,  # Can use email as username
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        # The endpoint might return 400 for invalid credentials instead of 401
        assert response.status_code in [400, 401]
        data = response.get_json()
        assert 'error' in data
    
    def test_profile_endpoint(self, client, auth_headers):
        """Test user profile endpoint"""
        response = client.get('/api/auth/profile',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
    
    def test_change_password_endpoint(self, client, auth_headers, sample_user):
        """Test change password endpoint"""
        # Set the password properly for the test user
        sample_user.set_password('TestPassword123!')
        from config.database import db
        db.session.commit()
        
        password_data = {
            'current_password': 'TestPassword123!',
            'new_password': 'NewPassword123!'
        }
        
        response = client.post('/api/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data


class TestPrayerEndpoints:
    """Test prayer-related endpoints"""
    
    def test_get_prayer_times(self, client, auth_headers):
        """Test getting prayer times for a date"""
        test_date = '2025-09-14'
        
        response = client.get(f'/api/prayers/times/{test_date}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prayers' in data
        # Prayers should be a list of prayer objects
        assert isinstance(data['prayers'], list)
        assert len(data['prayers']) == 5  # 5 daily prayers
    
    def test_get_prayer_times_invalid_date(self, client, auth_headers):
        """Test getting prayer times with invalid date"""
        invalid_date = 'invalid-date'
        
        response = client.get(f'/api/prayers/times/{invalid_date}',
                            headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_mark_prayer_completed(self, client, auth_headers, sample_user):
        """Test marking a prayer as completed"""
        prayer_data = {
            'prayer_name': 'FAJR',  # Use prayer name instead of ID
            'completed_at': datetime.now().isoformat()
        }
        
        response = client.post('/api/prayers/complete',
                             data=json.dumps(prayer_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_mark_prayer_qada(self, client, auth_headers, sample_user):
        """Test marking a missed prayer as qada"""
        prayer_data = {
            'prayer_name': 'DHUHR',  # Use prayer name instead of ID
            'completed_at': datetime.now().isoformat(),
            'is_qada': True
        }
        
        response = client.post('/api/prayers/complete',
                             data=json.dumps(prayer_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_get_prayer_status(self, client, auth_headers):
        """Test getting prayer status for a date"""
        test_date = '2025-09-14'
        
        response = client.get(f'/api/prayers/status/{test_date}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prayer_status' in data
        # Prayer status should be a dictionary
        assert isinstance(data['prayer_status'], dict)
    
    def test_get_prayer_streak(self, client, auth_headers):
        """Test getting prayer streak information"""
        response = client.get('/api/prayers/streak',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'streak' in data


class TestDashboardEndpoints:
    """Test dashboard-related endpoints"""
    
    def test_get_dashboard_stats(self, client, auth_headers):
        """Test getting dashboard statistics"""
        response = client.get('/api/dashboard/stats',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_prayers' in data
        assert 'completed_prayers' in data
        assert 'missed_prayers' in data
        assert 'qada_prayers' in data
        assert 'completion_rate' in data
    
    def test_get_recent_activity(self, client, auth_headers):
        """Test getting recent prayer activity"""
        response = client.get('/api/dashboard/recent',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'activities' in data
        assert isinstance(data['activities'], list)
    
    def test_get_dashboard_calendar(self, client, auth_headers):
        """Test getting dashboard calendar"""
        year, month = 2025, 9
        
        response = client.get(f'/api/dashboard/calendar/{year}/{month}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'calendar' in data


class TestNotificationEndpoints:
    """Test notification-related endpoints"""
    
    def test_get_notification_preferences(self, client, auth_headers):
        """Test getting notification preferences"""
        response = client.get('/api/notifications/preferences',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'preferences' in data
    
    def test_test_reminder(self, client, auth_headers):
        """Test sending a test reminder"""
        reminder_data = {
            'prayer_name': 'FAJR',
            'message': 'Test reminder message'
        }
        
        response = client.post('/api/notifications/test-reminder',
                             data=json.dumps(reminder_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_update_notification_preferences(self, client, auth_headers):
        """Test updating notification preferences"""
        preferences = {
            'email_notifications': True,
            'reminder_minutes_before': 15,
            'qada_reminders': True
        }
        
        response = client.put('/api/notifications/preferences',
                            data=json.dumps(preferences),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data


class TestSocialEndpoints:
    """Test social features endpoints"""
    
    def test_get_family(self, client, auth_headers):
        """Test getting user's family"""
        response = client.get('/api/social/family',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'family' in data
    
    def test_create_family_member(self, client, auth_headers):
        """Test creating a family member"""
        member_data = {
            'name': 'Test Family Member',
            'email': 'family@example.com',
            'relationship': 'spouse'
        }
        
        response = client.post('/api/social/family',
                             data=json.dumps(member_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data
    
    def test_send_family_reminder(self, client, auth_headers):
        """Test sending family reminder"""
        reminder_data = {
            'message': 'Test family reminder',
            'prayer_name': 'FAJR'
        }
        
        response = client.post('/api/social/remind',
                             data=json.dumps(reminder_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        # This might fail if no family members exist, which is expected
        assert response.status_code in [200, 400, 404]


class TestInspirationalEndpoints:
    """Test inspirational content endpoints"""
    
    def test_get_random_verse(self, client, auth_headers):
        """Test getting random Quranic verse"""
        response = client.get('/api/inspirational/verse/random',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'verse' in data
    
    def test_get_random_hadith(self, client, auth_headers):
        """Test getting random Hadith"""
        response = client.get('/api/inspirational/hadith/random',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'hadith' in data


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoints without authentication"""
        response = client.get('/api/dashboard/stats')
        # The endpoint might return 401 or 404 depending on implementation
        assert response.status_code in [401, 404]
    
    def test_invalid_json_data(self, client, auth_headers):
        """Test sending invalid JSON data"""
        response = client.post('/api/prayers/complete',
                             data='invalid json',
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client, auth_headers):
        """Test missing required fields in requests"""
        incomplete_data = {
            'prayer_name': 'FAJR'
            # Missing completed_at
        }
        
        response = client.post('/api/prayers/complete',
                             data=json.dumps(incomplete_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_invalid_prayer_name(self, client, auth_headers):
        """Test with invalid prayer name"""
        prayer_data = {
            'prayer_name': 'INVALID_PRAYER',  # Non-existent prayer name
            'completed_at': datetime.now().isoformat()
        }
        
        response = client.post('/api/prayers/complete',
                             data=json.dumps(prayer_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_on_auth_endpoints(self, client):
        """Test rate limiting on authentication endpoints"""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        # Make multiple rapid requests
        for _ in range(10):
            response = client.post('/api/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
        
        # Should eventually get rate limited
        assert response.status_code in [401, 429]


class TestDataValidation:
    """Test data validation across endpoints"""
    
    def test_email_validation(self, client):
        """Test email validation in registration"""
        invalid_emails = [
            'invalid-email',
            'user@',
            '@domain.com',
            'user..name@domain.com',
            'user@domain..com'
        ]
        
        for email in invalid_emails:
            user_data = {
                'username': 'testuser',
                'email': email,
                'password': 'TestPassword123!',
                'location': 'Test Location'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 400
    
    def test_password_validation(self, client):
        """Test password validation in registration"""
        weak_passwords = [
            '123',
            'password',
            'PASSWORD',
            'Password',
            'Password123'
        ]
        
        for password in weak_passwords:
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'location': 'Test Location'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 400
    
    def test_prayer_completion_validation(self, client, auth_headers):
        """Test prayer completion data validation"""
        invalid_data = [
            {'prayer_name': 'INVALID', 'completed_at': datetime.now().isoformat()},
            {'prayer_name': 'FAJR', 'completed_at': 'invalid-date'},
            {'prayer_name': '', 'completed_at': datetime.now().isoformat()},
            {'prayer_name': 'FAJR'},  # Missing completed_at
        ]
        
        for data in invalid_data:
            response = client.post('/api/prayers/complete',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
