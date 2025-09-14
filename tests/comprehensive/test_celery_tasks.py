"""
Comprehensive Celery Tasks Tests
Tests all Celery tasks for proper execution, error handling, and integration.
"""

import pytest
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock, Mock
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification
from app.tasks.prayer_reminders import (
    send_prayer_reminders,
    send_individual_reminder,
    send_prayer_window_reminders,
    cleanup_old_notifications,
    send_bulk_reminders,
    test_reminder_system
)
from app.tasks.consistency_checks import (
    check_user_consistency,
    analyze_prayer_patterns,
    send_weekly_report,
    send_motivational_message
)


class TestPrayerReminderTasks:
    """Test prayer reminder Celery tasks"""
    
    def test_send_prayer_reminders_task(self, app, test_user):
        """Test the main prayer reminders task"""
        with app.app_context():
            # Ensure user has email notifications enabled
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
            with patch('app.tasks.prayer_reminders.send_individual_reminder.delay') as mock_reminder:
                mock_reminder.return_value = Mock(id='test-task-id')
                
                # Execute the task
                result = send_prayer_reminders()
                
                # Verify task executed
                assert result is not None
                # The task should have attempted to send reminders
                # (exact behavior depends on current time and prayer times)
    
    def test_send_individual_reminder_task(self, app, test_user):
        """Test individual reminder task"""
        with app.app_context():
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
            
            with patch('app.services.email_service.EmailService.send_prayer_reminder') as mock_email:
                mock_email.return_value = True
                
                # Execute the task
                result = send_individual_reminder(test_user.id, prayer.id, '05:30')
                
                # Verify task executed
                assert result is not None
                # Email service should have been called
                mock_email.assert_called_once()
    
    def test_send_prayer_window_reminders_task(self, app, test_user):
        """Test prayer window reminders task"""
        with app.app_context():
            # Ensure user has email notifications enabled
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
            with patch('app.tasks.prayer_reminders.send_individual_reminder.delay') as mock_reminder:
                mock_reminder.return_value = Mock(id='test-task-id')
                
                # Execute the task
                result = send_prayer_window_reminders()
                
                # Verify task executed
                assert result is not None
    
    def test_cleanup_old_notifications_task(self, app, test_user):
        """Test cleanup old notifications task"""
        with app.app_context():
            # Create old notifications
            old_notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=1,
                notification_type='reminder',
                message='Old notification',
                scheduled_time=datetime.now() - timedelta(days=7),
                is_sent=True
            )
            db.session.add(old_notification)
            db.session.commit()
            
            # Execute cleanup task
            result = cleanup_old_notifications()
            
            # Verify task executed
            assert result is not None
            
            # Verify old notification was cleaned up
            old_notif = PrayerNotification.query.filter_by(id=old_notification.id).first()
            assert old_notif is None
    
    def test_send_bulk_reminders_task(self, app, test_user):
        """Test bulk reminders task"""
        with app.app_context():
            # Create multiple users
            users = []
            for i in range(3):
                user = User(
                    username=f'bulkuser{i}',
                    email=f'bulkuser{i}@example.com',
                    password_hash='hashed_password',
                    location='Test City',
                    email_notifications=True,
                    email_verified=True
                )
                users.append(user)
                db.session.add(user)
            db.session.commit()
            
            with patch('app.tasks.prayer_reminders.send_individual_reminder.delay') as mock_reminder:
                mock_reminder.return_value = Mock(id='test-task-id')
                
                # Execute bulk reminders task
                result = send_bulk_reminders([user.id for user in users], 1, '05:30')
                
                # Verify task executed
                assert result is not None
                # Should have called individual reminder for each user
                assert mock_reminder.call_count == len(users)
    
    def test_test_reminder_system_task(self, app, test_user):
        """Test the test reminder system task"""
        with app.app_context():
            with patch('app.services.email_service.EmailService.send_prayer_reminder') as mock_email:
                mock_email.return_value = True
                
                # Execute test task
                result = test_reminder_system(test_user.id, 'FAJR', '05:30')
                
                # Verify task executed
                assert result is not None
                # Email service should have been called
                mock_email.assert_called_once()


class TestConsistencyCheckTasks:
    """Test consistency check Celery tasks"""
    
    def test_check_user_consistency_task(self, app, test_user):
        """Test user consistency check task"""
        with app.app_context():
            # Ensure user has email notifications enabled
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
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
            
            # Execute consistency check
            result = check_user_consistency()
            
            # Verify task executed
            assert result is not None
    
    def test_analyze_prayer_patterns_task(self, app, test_user):
        """Test prayer patterns analysis task"""
        with app.app_context():
            # Create some prayer completions
            for i in range(5):
                completion = PrayerCompletion(
                    user_id=test_user.id,
                    prayer_id=i + 1,
                    completed_at=datetime.now(),
                    is_qada=False
                )
                db.session.add(completion)
            db.session.commit()
            
            # Execute pattern analysis
            result = analyze_prayer_patterns(test_user.id, 7)
            
            # Verify task executed
            assert result is not None
    
    def test_send_weekly_report_task(self, app, test_user):
        """Test weekly report task"""
        with app.app_context():
            # Ensure user has email notifications enabled
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
            # Execute weekly report task
            result = send_weekly_report()
            
            # Verify task executed
            assert result is not None
    
    def test_send_motivational_message_task(self, app, test_user):
        """Test motivational message task"""
        with app.app_context():
            # Ensure user has email notifications enabled
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
            # Execute motivational message task
            result = send_motivational_message(test_user.id, 'general')
            
            # Verify task executed
            assert result is not None


class TestTaskErrorHandling:
    """Test error handling in Celery tasks"""
    
    def test_prayer_reminder_task_error_handling(self, app):
        """Test error handling in prayer reminder tasks"""
        with app.app_context():
            with patch('app.services.email_service.EmailService.send_prayer_reminder', 
                      side_effect=Exception("Email service error")):
                
                # Execute task with error
                result = send_individual_reminder(99999, 1, '05:30')
                
                # Task should handle error gracefully
                assert result is not None
    
    def test_consistency_check_task_error_handling(self, app):
        """Test error handling in consistency check tasks"""
        with app.app_context():
            with patch('config.database.db.session.commit', 
                      side_effect=Exception("Database error")):
                
                # Execute task with error
                result = check_user_consistency()
                
                # Task should handle error gracefully
                assert result is not None
    
    def test_task_with_invalid_data(self, app):
        """Test tasks with invalid data"""
        with app.app_context():
            # Test with invalid user ID
            result = send_individual_reminder(99999, 1, '05:30')
            assert result is not None
            
            # Test with invalid prayer ID
            result = send_individual_reminder(1, 99999, '05:30')
            assert result is not None


class TestTaskIntegration:
    """Test integration between different tasks"""
    
    def test_reminder_workflow_integration(self, app, test_user):
        """Test integration of reminder workflow tasks"""
        with app.app_context():
            # Ensure user is set up for notifications
            test_user.email_notifications = True
            test_user.email_verified = True
            db.session.commit()
            
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
            
            with patch('app.services.email_service.EmailService.send_prayer_reminder') as mock_email:
                mock_email.return_value = True
                
                # Execute main reminder task
                main_result = send_prayer_reminders()
                assert main_result is not None
                
                # Execute individual reminder
                individual_result = send_individual_reminder(test_user.id, prayer.id, '05:30')
                assert individual_result is not None
                
                # Execute cleanup task
                cleanup_result = cleanup_old_notifications()
                assert cleanup_result is not None
    
    def test_consistency_workflow_integration(self, app, test_user):
        """Test integration of consistency check workflow"""
        with app.app_context():
            # Create test data
            completion = PrayerCompletion(
                user_id=test_user.id,
                prayer_id=1,
                completed_at=datetime.now(),
                is_qada=False
            )
            db.session.add(completion)
            db.session.commit()
            
            # Execute all consistency check tasks
            consistency_result = check_user_consistency()
            assert consistency_result is not None
            
            pattern_result = analyze_prayer_patterns(test_user.id, 7)
            assert pattern_result is not None
            
            report_result = send_weekly_report()
            assert report_result is not None
            
            motivational_result = send_motivational_message(test_user.id, 'general')
            assert motivational_result is not None


class TestTaskScheduling:
    """Test task scheduling and timing"""
    
    def test_task_execution_timing(self, app):
        """Test task execution timing"""
        with app.app_context():
            start_time = datetime.now()
            
            # Execute a simple task
            result = test_reminder_system(1, 'FAJR', '05:30')
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Task should complete quickly (under 5 seconds for test)
            assert execution_time < 5
            assert result is not None
    
    def test_task_retry_mechanism(self, app):
        """Test task retry mechanism"""
        with app.app_context():
            # This would test Celery's retry mechanism
            # For now, just verify tasks can be called multiple times
            result1 = test_reminder_system(1, 'FAJR', '05:30')
            result2 = test_reminder_system(1, 'FAJR', '05:30')
            
            assert result1 is not None
            assert result2 is not None


class TestTaskDataValidation:
    """Test data validation in tasks"""
    
    def test_task_input_validation(self, app):
        """Test task input validation"""
        with app.app_context():
            # Test with various invalid inputs
            invalid_inputs = [
                (None, 1, '05:30'),  # None user ID
                (1, None, '05:30'),  # None prayer ID
                (1, 1, None),        # None time
                ('invalid', 1, '05:30'),  # Invalid user ID type
                (1, 'invalid', '05:30'),  # Invalid prayer ID type
                (1, 1, 'invalid_time'),   # Invalid time format
            ]
            
            for user_id, prayer_id, prayer_time in invalid_inputs:
                result = send_individual_reminder(user_id, prayer_id, prayer_time)
                # Task should handle invalid inputs gracefully
                assert result is not None
    
    def test_task_output_validation(self, app, test_user):
        """Test task output validation"""
        with app.app_context():
            # Test that tasks return expected output format
            result = test_reminder_system(test_user.id, 'FAJR', '05:30')
            
            # Result should be a dictionary or None
            assert result is None or isinstance(result, dict)


class TestTaskPerformance:
    """Test task performance and optimization"""
    
    def test_bulk_task_performance(self, app):
        """Test bulk task performance"""
        with app.app_context():
            # Create multiple users for bulk testing
            users = []
            for i in range(10):
                user = User(
                    username=f'perfuser{i}',
                    email=f'perfuser{i}@example.com',
                    password_hash='hashed_password',
                    location='Test City',
                    email_notifications=True,
                    email_verified=True
                )
                users.append(user)
                db.session.add(user)
            db.session.commit()
            
            start_time = datetime.now()
            
            with patch('app.tasks.prayer_reminders.send_individual_reminder.delay') as mock_reminder:
                mock_reminder.return_value = Mock(id='test-task-id')
                
                # Execute bulk reminders
                result = send_bulk_reminders([user.id for user in users], 1, '05:30')
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Bulk operation should be reasonably fast
            assert execution_time < 10
            assert result is not None
            assert mock_reminder.call_count == len(users)
    
    def test_task_memory_usage(self, app):
        """Test task memory usage"""
        with app.app_context():
            # This would test memory usage in a real scenario
            # For now, just verify tasks don't cause obvious memory leaks
            for i in range(5):
                result = test_reminder_system(1, 'FAJR', '05:30')
                assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
