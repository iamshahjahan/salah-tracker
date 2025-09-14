"""
Comprehensive Frontend Functionality Tests
Tests frontend JavaScript functionality, API integration, and user interactions.
"""

import pytest
import json
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion


class TestFrontendAPI:
    """Test frontend API integration"""
    
    def test_home_page_loads(self, client):
        """Test that home page loads correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
        assert b'<title>' in response.data
    
    def test_static_files_served(self, client):
        """Test that static files are served correctly"""
        # Test CSS file
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
        
        # Test JavaScript files
        js_files = ['app.js', 'auth.js', 'prayer.js', 'dashboard.js']
        for js_file in js_files:
            response = client.get(f'/static/js/{js_file}')
            assert response.status_code == 200
            assert 'javascript' in response.content_type
    
    def test_api_endpoints_accessible(self, client, auth_headers):
        """Test that all API endpoints are accessible"""
        endpoints = [
            '/api/health',
            '/api/dashboard/stats',
            '/api/prayer/times/2025-09-14',
            '/api/notifications',
            '/api/inspirational/content'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            assert response.status_code in [200, 401]  # 401 for protected endpoints without auth
    
    def test_cors_headers(self, client):
        """Test CORS headers for API endpoints"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        # Check for CORS headers (if implemented)
        # This would depend on your CORS configuration
        # assert 'Access-Control-Allow-Origin' in response.headers


class TestAuthenticationFlow:
    """Test authentication flow from frontend perspective"""
    
    def test_login_form_submission(self, client, test_user):
        """Test login form submission"""
        login_data = {
            'email': test_user.email,
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
    
    def test_registration_form_submission(self, client):
        """Test registration form submission"""
        user_data = {
            'username': 'frontenduser',
            'email': 'frontenduser@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Frontend',
            'last_name': 'User',
            'location': 'Test City',
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data
    
    def test_logout_functionality(self, client, auth_headers):
        """Test logout functionality"""
        response = client.post('/api/auth/logout',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_token_refresh(self, client, auth_headers):
        """Test token refresh functionality"""
        response = client.post('/api/auth/refresh',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data


class TestPrayerFunctionality:
    """Test prayer-related frontend functionality"""
    
    def test_get_prayer_times_api(self, client, auth_headers):
        """Test getting prayer times via API"""
        test_date = '2025-09-14'
        
        response = client.get(f'/api/prayer/times/{test_date}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prayer_times' in data
        assert len(data['prayer_times']) == 5
    
    def test_mark_prayer_completed_api(self, client, auth_headers, test_user):
        """Test marking prayer as completed via API"""
        prayer_data = {
            'prayer_id': 1,
            'completed_at': datetime.now().isoformat()
        }
        
        response = client.post('/api/prayer/complete',
                             data=json.dumps(prayer_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'completion' in data
    
    def test_get_prayer_status_api(self, client, auth_headers):
        """Test getting prayer status via API"""
        test_date = '2025-09-14'
        
        response = client.get(f'/api/prayer/status/{test_date}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prayer_status' in data
        assert len(data['prayer_status']) == 5
    
    def test_prayer_calendar_api(self, client, auth_headers):
        """Test prayer calendar API"""
        year, month = 2025, 9
        
        response = client.get(f'/api/prayer/calendar/{year}/{month}',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'calendar' in data
        assert 'month' in data
        assert 'year' in data


class TestDashboardFunctionality:
    """Test dashboard functionality"""
    
    def test_dashboard_stats_api(self, client, auth_headers):
        """Test dashboard statistics API"""
        response = client.get('/api/dashboard/stats',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_prayers' in data
        assert 'completed_prayers' in data
        assert 'missed_prayers' in data
        assert 'qada_prayers' in data
        assert 'completion_rate' in data
    
    def test_recent_activity_api(self, client, auth_headers):
        """Test recent activity API"""
        response = client.get('/api/dashboard/recent-activity',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'activities' in data
        assert isinstance(data['activities'], list)
    
    def test_prayer_streak_api(self, client, auth_headers):
        """Test prayer streak API"""
        response = client.get('/api/dashboard/streak',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'current_streak' in data
        assert 'longest_streak' in data
        assert 'streak_start_date' in data


class TestNotificationFunctionality:
    """Test notification functionality"""
    
    def test_get_notifications_api(self, client, auth_headers):
        """Test getting notifications API"""
        response = client.get('/api/notifications',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'notifications' in data
        assert isinstance(data['notifications'], list)
    
    def test_notification_preferences_api(self, client, auth_headers):
        """Test notification preferences API"""
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


class TestSocialFunctionality:
    """Test social features functionality"""
    
    def test_family_groups_api(self, client, auth_headers):
        """Test family groups API"""
        response = client.get('/api/social/family-groups',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'family_groups' in data
        assert isinstance(data['family_groups'], list)
    
    def test_create_family_group_api(self, client, auth_headers):
        """Test creating family group API"""
        group_data = {
            'name': 'Test Family',
            'description': 'Test family group'
        }
        
        response = client.post('/api/social/family-groups',
                             data=json.dumps(group_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data


class TestInspirationalContent:
    """Test inspirational content functionality"""
    
    def test_inspirational_content_api(self, client, auth_headers):
        """Test inspirational content API"""
        response = client.get('/api/inspirational/content',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'content' in data
        assert 'type' in data
    
    def test_daily_quote_api(self, client, auth_headers):
        """Test daily quote API"""
        response = client.get('/api/inspirational/quote',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'quote' in data
        assert 'author' in data


class TestErrorHandling:
    """Test error handling in frontend"""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints"""
        protected_endpoints = [
            '/api/dashboard/stats',
            '/api/prayer/times/2025-09-14',
            '/api/notifications',
            '/api/social/family-groups'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_invalid_json_requests(self, client, auth_headers):
        """Test handling of invalid JSON requests"""
        response = client.post('/api/prayer/complete',
                             data='invalid json',
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        incomplete_data = {
            'prayer_id': 1
            # Missing completed_at
        }
        
        response = client.post('/api/prayer/complete',
                             data=json.dumps(incomplete_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_invalid_date_formats(self, client, auth_headers):
        """Test handling of invalid date formats"""
        invalid_dates = ['invalid-date', '2025-13-01', '2025-02-30']
        
        for invalid_date in invalid_dates:
            response = client.get(f'/api/prayer/times/{invalid_date}',
                                headers=auth_headers)
            assert response.status_code == 400


class TestDataValidation:
    """Test data validation in frontend"""
    
    def test_email_validation(self, client):
        """Test email validation in registration"""
        invalid_emails = [
            'invalid-email',
            'user@',
            '@domain.com',
            'user..name@domain.com'
        ]
        
        for email in invalid_emails:
            user_data = {
                'username': 'testuser',
                'email': email,
                'password': 'TestPassword123!',
                'first_name': 'Test',
                'last_name': 'User',
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
            'Password'
        ]
        
        for password in weak_passwords:
            user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'first_name': 'Test',
                'last_name': 'User',
                'location': 'Test Location'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 400
    
    def test_prayer_id_validation(self, client, auth_headers):
        """Test prayer ID validation"""
        invalid_prayer_ids = [0, 6, -1, 'invalid']
        
        for prayer_id in invalid_prayer_ids:
            prayer_data = {
                'prayer_id': prayer_id,
                'completed_at': datetime.now().isoformat()
            }
            
            response = client.post('/api/prayer/complete',
                                 data=json.dumps(prayer_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            assert response.status_code == 400


class TestPerformance:
    """Test frontend performance"""
    
    def test_api_response_times(self, client, auth_headers):
        """Test API response times"""
        import time
        
        endpoints = [
            '/api/health',
            '/api/dashboard/stats',
            '/api/prayer/times/2025-09-14',
            '/api/notifications'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # API should respond within 2 seconds
            assert response_time < 2
            assert response.status_code in [200, 401]
    
    def test_concurrent_requests(self, client, auth_headers):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get('/api/health', headers=auth_headers)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 5
        assert all(status == 200 for status in results)


class TestSecurity:
    """Test security aspects of frontend"""
    
    def test_sql_injection_protection(self, client, auth_headers):
        """Test protection against SQL injection"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'hacker@evil.com'); --"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in various fields
            user_data = {
                'username': malicious_input,
                'email': 'test@example.com',
                'password': 'TestPassword123!',
                'location': 'Test Location'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            # Should not cause server error (500)
            assert response.status_code != 500
    
    def test_xss_protection(self, client, auth_headers):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            user_data = {
                'username': payload,
                'email': 'test@example.com',
                'password': 'TestPassword123!',
                'location': 'Test Location'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            # Should not cause server error
            assert response.status_code != 500
            
            # Check that payload is sanitized in response
            if response.status_code == 200:
                response_data = response.get_json()
                # Payload should be sanitized
                assert '<script>' not in str(response_data)
                assert 'javascript:' not in str(response_data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
