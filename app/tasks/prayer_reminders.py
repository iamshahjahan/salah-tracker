"""
Prayer reminder tasks for Celery.

This module contains Celery tasks for sending prayer reminders,
managing notification schedules, and handling prayer-related background jobs.
"""

from celery import current_task
from datetime import datetime, timedelta, time
import pytz
from typing import List, Dict, Any

from celery_config import celery_app
from main import app
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification
from app.services.notification_service import NotificationService
from app.services.prayer_service import PrayerService
from database import db
from logging_config import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_prayer_reminders')
def send_prayer_reminders(self):
    """
    Send prayer reminders to all users who have notifications enabled.
    
    This task runs every 5 minutes and checks for users who need
    prayer reminders based on their reminder preferences.
    """
    with app.app_context():
        try:
            logger.info("Starting prayer reminders task")
            # Get current time in UTC
            now_utc = datetime.utcnow()
            logger.info(f"Current UTC time: {now_utc}")
            
            # Get all users with email notifications enabled
            users = User.query.filter_by(
                email_notifications=True,
                notification_enabled=True,
                email_verified=True
            ).all()
            
            logger.info(f"Found {len(users)} eligible users for reminders")
            total_reminders_sent = 0
            total_errors = 0
            
            for user in users:
                try:
                    logger.info(f"Processing user: {user.email} (ID: {user.id})")
                    # Get user's timezone
                    user_tz = pytz.timezone(user.timezone or 'UTC')
                    now_user_tz = now_utc.replace(tzinfo=pytz.UTC).astimezone(user_tz)
                    logger.info(f"User timezone: {user.timezone}, Current user time: {now_user_tz}")
                    
                    # Get today's prayer times for the user
                    from app.config.settings import get_config
                    config = get_config()
                    prayer_service = PrayerService(config)
                    prayer_times_result = prayer_service.get_prayer_times(user.id, now_user_tz.date().strftime('%Y-%m-%d'))
                    prayer_times = prayer_times_result.get('prayer_times', {}) if prayer_times_result.get('success') else {}
                    
                    if not prayer_times:
                        continue
                    
                    # Check each prayer time
                    for prayer_type, prayer_time_str in prayer_times.items():
                        # Parse prayer time
                        prayer_time = datetime.strptime(prayer_time_str, '%H:%M').time()
                        prayer_datetime = datetime.combine(now_user_tz.date(), prayer_time)
                        prayer_datetime = user_tz.localize(prayer_datetime)
                        
                        # Get user's reminder time for this prayer
                        reminder_minutes = user.reminder_times.get(prayer_type.lower(), 10)
                        reminder_time = prayer_datetime - timedelta(minutes=reminder_minutes)
                        
                        # Check if it's time to send reminder (within 5-minute window)
                        time_diff = abs((now_user_tz - reminder_time).total_seconds())
                        
                        if time_diff <= 300:  # 5 minutes window
                            # Check if we already sent a reminder for this prayer today
                            existing_notification = PrayerNotification.query.filter_by(
                                user_id=user.id,
                                prayer_type=prayer_type.lower(),
                                prayer_date=now_user_tz.date(),
                                notification_type='reminder'
                            ).first()
                            
                            if not existing_notification:
                                # Send reminder
                                notification_service = NotificationService(config)
                                result = notification_service.send_prayer_reminder(
                                    user, prayer_type.lower(), prayer_datetime
                                )
                                
                                if result.get('success'):
                                    total_reminders_sent += 1
                                    current_task.update_state(
                                        state='PROGRESS',
                                        meta={
                                            'current_user': user.email,
                                            'prayer_type': prayer_type,
                                            'reminders_sent': total_reminders_sent,
                                            'errors': total_errors
                                        }
                                    )
                                else:
                                    total_errors += 1
                                    logger.error(f"Failed to send reminder to {user.email}: {result.get('error')}")
                
                except Exception as e:
                    total_errors += 1
                    logger.error(f"Error processing user {user.email}: {str(e)}")
                    continue
            
            result = {
                'status': 'completed',
                'reminders_sent': total_reminders_sent,
                'errors': total_errors,
                'total_users_processed': len(users),
                'timestamp': now_utc.isoformat()
            }
            logger.info(f"Prayer reminders task completed: {result}")
            return result
            
        except Exception as e:
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_individual_reminder')
def send_individual_reminder(self, user_id: int, prayer_type: str, prayer_time: str):
    """
    Send a prayer reminder to a specific user for a specific prayer.
    
    Args:
        user_id: ID of the user to send reminder to
        prayer_type: Type of prayer (fajr, dhuhr, asr, maghrib, isha)
        prayer_time: Time of the prayer in HH:MM format
    """
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                return {'status': 'error', 'message': 'User not found'}
            
            if not user.email_notifications:
                return {'status': 'skipped', 'message': 'User has disabled email notifications'}
            
            # Parse prayer time
            prayer_time_obj = datetime.strptime(prayer_time, '%H:%M').time()
            user_tz = pytz.timezone(user.timezone or 'UTC')
            prayer_datetime = datetime.combine(datetime.utcnow().date(), prayer_time_obj)
            prayer_datetime = user_tz.localize(prayer_datetime)
            
            # Send reminder
            from app.config.settings import get_config
            config = get_config()
            notification_service = NotificationService(config)
            result = notification_service.send_prayer_reminder(
                user, prayer_type, prayer_datetime
            )
            
            return {
                'status': 'completed' if result.get('success') else 'failed',
                'user_id': user_id,
                'prayer_type': prayer_type,
                'result': result
            }
            
        except Exception as e:
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.cleanup_old_notifications')
def cleanup_old_notifications(self, days_old: int = 30):
    """
    Clean up old prayer notifications to keep the database clean.
    
    Args:
        days_old: Number of days old notifications to delete (default: 30)
    """
    with app.app_context():
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old notifications
            deleted_count = PrayerNotification.query.filter(
                PrayerNotification.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            return {
                'status': 'completed',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_bulk_reminders')
def send_bulk_reminders(self, user_ids: List[int], prayer_type: str, prayer_time: str):
    """
    Send prayer reminders to multiple users at once.
    
    Args:
        user_ids: List of user IDs to send reminders to
        prayer_type: Type of prayer
        prayer_time: Time of the prayer
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for user_id in user_ids:
            try:
                result = send_individual_reminder.delay(user_id, prayer_type, prayer_time)
                results.append({
                    'user_id': user_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
                successful += 1
                
            except Exception as e:
                results.append({
                    'user_id': user_id,
                    'status': 'failed',
                    'error': str(e)
                })
                failed += 1
        
        return {
            'status': 'completed',
            'total_users': len(user_ids),
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.test_reminder_system')
def test_reminder_system(self):
    """
    Test the reminder system by sending a test reminder to all users.
    This is useful for testing the email system and notification flow.
    """
    try:
        users = User.query.filter_by(
            email_notifications=True,
            email_verified=True
        ).limit(5).all()  # Limit to 5 users for testing
        
        results = []
        
        for user in users:
            try:
                # Send test reminder for Dhuhr prayer
                result = send_individual_reminder.delay(
                    user.id, 'dhuhr', '12:00'
                )
                
                results.append({
                    'user_id': user.id,
                    'user_email': user.email,
                    'task_id': result.id,
                    'status': 'queued'
                })
                
            except Exception as e:
                results.append({
                    'user_id': user.id,
                    'user_email': user.email,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'status': 'completed',
            'test_type': 'reminder_system',
            'users_tested': len(users),
            'results': results
        }
        
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
