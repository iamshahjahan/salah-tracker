"""
Test cases for email notification functionality.

This module contains comprehensive tests for the email notification system,
including prayer reminders, email templates, and notification service.
"""

import pytest
from datetime import datetime, time, date
from unittest.mock import patch, MagicMock
from app.models.user import User
from app.models.inspirational_content import QuranicVerse, Hadith
from app.services.notification_service import NotificationService
from app.services.email_service import EmailService
from app.services.email_templates import (
    get_prayer_reminder_template,
    get_prayer_name_arabic,
    get_prayer_name_english
)


class TestEmailNotifications:
    """Test cases for email notification functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True,
            language='en'
        )
        
        self.test_verse = QuranicVerse(
            id=1,
            verse_text='Test verse text',
            chapter='2',
            verse_number='255',
            translation='Test translation'
        )
        
        self.test_hadith = Hadith(
            id=1,
            text='Test hadith text',
            source='Test source',
            narrator='Test narrator'
        )

    def test_prayer_name_arabic(self):
        """Test Arabic prayer name conversion."""
        assert get_prayer_name_arabic('FAJR') == 'الفجر'
        assert get_prayer_name_arabic('DHUHR') == 'الظهر'
        assert get_prayer_name_arabic('ASR') == 'العصر'
        assert get_prayer_name_arabic('MAGHRIB') == 'المغرب'
        assert get_prayer_name_arabic('ISHA') == 'العشاء'

    def test_prayer_name_english(self):
        """Test English prayer name conversion."""
        assert get_prayer_name_english('FAJR') == 'Fajr'
        assert get_prayer_name_english('DHUHR') == 'Dhuhr'
        assert get_prayer_name_english('ASR') == 'Asr'
        assert get_prayer_name_english('MAGHRIB') == 'Maghrib'
        assert get_prayer_name_english('ISHA') == 'Isha'

    def test_arabic_prayer_reminder_template(self):
        """Test Arabic prayer reminder email template generation."""
        prayer_time = datetime.combine(date.today(), time(5, 30))
        completion_link = 'https://example.com/complete/123'
        
        template = get_prayer_reminder_template(
            self.test_user, 'FAJR', prayer_time, self.test_verse, self.test_hadith, completion_link
        )
        
        # Check that template contains essential elements
        assert 'الفجر' in template  # Arabic prayer name
        assert '05:30' in template  # Prayer time
        assert 'Test verse text' in template  # Verse content
        assert 'Test hadith text' in template  # Hadith content
        assert completion_link in template  # Completion link
        assert 'dir="rtl"' in template  # RTL direction for Arabic

    def test_english_prayer_reminder_template(self):
        """Test English prayer reminder email template generation."""
        # Set user language to English
        self.test_user.language = 'en'
        
        prayer_time = datetime.combine(date.today(), time(5, 30))
        completion_link = 'https://example.com/complete/123'
        
        template = get_prayer_reminder_template(
            self.test_user, 'FAJR', prayer_time, self.test_verse, self.test_hadith, completion_link
        )
        
        # Check that template contains essential elements
        assert 'Fajr' in template  # English prayer name
        assert '05:30' in template  # Prayer time
        assert 'Test verse text' in template  # Verse content
        assert 'Test hadith text' in template  # Hadith content
        assert completion_link in template  # Completion link
        assert 'lang="en"' in template  # English language

    @patch('app.services.notification_service.EmailService')
    def test_send_prayer_reminder_success(self, mock_email_service):
        """Test successful prayer reminder email sending."""
        # Mock the email service
        mock_email_instance = MagicMock()
        mock_email_instance._send_email.return_value = True
        mock_email_service.return_value = mock_email_instance
        
        # Create notification service with mocked dependencies
        notification_service = NotificationService()
        notification_service.email_service = mock_email_instance
        
        # Mock database operations
        with patch.object(notification_service, 'create_record') as mock_create, \
             patch.object(notification_service, 'db_session') as mock_session:
            
            # Mock the notification record creation
            mock_notification = MagicMock()
            mock_notification.id = 1
            mock_create.return_value = mock_notification
            
            # Test sending prayer reminder
            prayer_time = datetime.combine(date.today(), time(5, 30))
            result = notification_service.send_prayer_reminder(
                self.test_user, 'FAJR', prayer_time
            )
            
            # Verify the result
            assert result['success'] is True
            assert 'notification_id' in result
            assert result['notification_id'] == 1
            
            # Verify email was sent
            mock_email_instance._send_email.assert_called_once()
            call_args = mock_email_instance._send_email.call_args
            assert call_args[0][0] == 'test@example.com'  # Email address
            assert 'Fajr' in call_args[0][1]  # Subject contains prayer name

    @patch('app.services.notification_service.EmailService')
    def test_send_prayer_reminder_email_failure(self, mock_email_service):
        """Test prayer reminder email sending failure."""
        # Mock the email service to return failure
        mock_email_instance = MagicMock()
        mock_email_instance._send_email.return_value = False
        mock_email_service.return_value = mock_email_instance
        
        # Create notification service with mocked dependencies
        notification_service = NotificationService()
        notification_service.email_service = mock_email_instance
        
        # Mock database operations
        with patch.object(notification_service, 'create_record') as mock_create:
            # Mock the notification record creation
            mock_notification = MagicMock()
            mock_notification.id = 1
            mock_create.return_value = mock_notification
            
            # Test sending prayer reminder
            prayer_time = datetime.combine(date.today(), time(5, 30))
            result = notification_service.send_prayer_reminder(
                self.test_user, 'FAJR', prayer_time
            )
            
            # Verify the result
            assert result['success'] is False
            assert 'error' in result
            assert 'Failed to send prayer reminder email' in result['error']

    def test_send_prayer_reminder_unverified_email(self):
        """Test prayer reminder sending to unverified email."""
        # Set user email as unverified
        self.test_user.email_verified = False
        
        notification_service = NotificationService()
        
        prayer_time = datetime.combine(date.today(), time(5, 30))
        result = notification_service.send_prayer_reminder(
            self.test_user, 'FAJR', prayer_time
        )
        
        # Verify the result
        assert result['success'] is False
        assert 'error' in result
        assert 'Email not verified' in result['error']

    def test_send_prayer_reminder_invalid_prayer_type(self):
        """Test prayer reminder with invalid prayer type."""
        notification_service = NotificationService()
        
        prayer_time = datetime.combine(date.today(), time(5, 30))
        result = notification_service.send_prayer_reminder(
            self.test_user, 'INVALID', prayer_time
        )
        
        # Verify the result
        assert result['success'] is False
        assert 'error' in result

    @patch('app.services.notification_service.EmailService')
    def test_send_prayer_reminder_with_verse_and_hadith(self, mock_email_service):
        """Test prayer reminder with inspirational content."""
        # Mock the email service
        mock_email_instance = MagicMock()
        mock_email_instance._send_email.return_value = True
        mock_email_service.return_value = mock_email_instance
        
        # Create notification service with mocked dependencies
        notification_service = NotificationService()
        notification_service.email_service = mock_email_instance
        
        # Mock database operations
        with patch.object(notification_service, 'create_record') as mock_create, \
             patch.object(notification_service, 'db_session') as mock_session:
            
            # Mock the notification record creation
            mock_notification = MagicMock()
            mock_notification.id = 1
            mock_create.return_value = mock_notification
            
            # Test sending prayer reminder
            prayer_time = datetime.combine(date.today(), time(5, 30))
            result = notification_service.send_prayer_reminder(
                self.test_user, 'FAJR', prayer_time
            )
            
            # Verify the result
            assert result['success'] is True
            
            # Verify email was sent with inspirational content
            mock_email_instance._send_email.assert_called_once()
            call_args = mock_email_instance._send_email.call_args
            email_content = call_args[0][2]  # Email body
            
            # Check that inspirational content is included
            assert 'Test verse text' in email_content
            assert 'Test hadith text' in email_content

    def test_email_template_language_switching(self):
        """Test that email templates switch language based on user preference."""
        prayer_time = datetime.combine(date.today(), time(5, 30))
        completion_link = 'https://example.com/complete/123'
        
        # Test Arabic template
        self.test_user.language = 'ar'
        arabic_template = get_prayer_reminder_template(
            self.test_user, 'FAJR', prayer_time, self.test_verse, self.test_hadith, completion_link
        )
        assert 'الفجر' in arabic_template
        assert 'dir="rtl"' in arabic_template
        
        # Test English template
        self.test_user.language = 'en'
        english_template = get_prayer_reminder_template(
            self.test_user, 'FAJR', prayer_time, self.test_verse, self.test_hadith, completion_link
        )
        assert 'Fajr' in english_template
        assert 'lang="en"' in english_template

    def test_prayer_reminder_datetime_handling(self):
        """Test that prayer reminder handles datetime objects correctly."""
        # Test with different datetime formats
        test_times = [
            datetime.combine(date.today(), time(5, 30)),  # Morning
            datetime.combine(date.today(), time(12, 15)),  # Noon
            datetime.combine(date.today(), time(18, 45)),  # Evening
        ]
        
        for prayer_time in test_times:
            template = get_prayer_reminder_template(
                self.test_user, 'FAJR', prayer_time, self.test_verse, self.test_hadith, 'test-link'
            )
            
            # Verify that the time is properly formatted in the template
            time_str = prayer_time.strftime('%H:%M')
            assert time_str in template


class TestEmailServiceIntegration:
    """Integration tests for email service functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            email_verified=True,
            language='en'
        )

    @patch('app.services.email_service.smtplib.SMTP')
    def test_email_service_send_email_success(self, mock_smtp):
        """Test successful email sending through email service."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Create email service
        email_service = EmailService()
        
        # Test sending email
        result = email_service._send_email(
            'test@example.com',
            'Test Subject',
            '<html><body>Test content</body></html>'
        )
        
        # Verify the result
        assert result is True
        mock_server.send_message.assert_called_once()

    @patch('app.services.email_service.smtplib.SMTP')
    def test_email_service_send_email_failure(self, mock_smtp):
        """Test email sending failure through email service."""
        # Mock SMTP server to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        # Create email service
        email_service = EmailService()
        
        # Test sending email
        result = email_service._send_email(
            'test@example.com',
            'Test Subject',
            '<html><body>Test content</body></html>'
        )
        
        # Verify the result
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
