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
    Send prayer reminders to users for prayers in pending state.
    
    This task runs every 5 minutes and checks for users who have
    prayers in pending state (during prayer time) that are not completed.
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
                    
                    # Get today's prayer data with status information for the user
                    from app.config.settings import get_config
                    config = get_config()
                    prayer_service = PrayerService(config)
                    prayer_times_result = prayer_service.get_prayer_times(user.id, now_user_tz.date().strftime('%Y-%m-%d'))
                    prayer_data_list = prayer_times_result.get('prayers', []) if prayer_times_result.get('success') else []
                    
                    if not prayer_data_list:
                        logger.info(f"No prayer data found for {user.email}")
                        continue
                    
                    # Check each prayer for pending status
                    for prayer_data in prayer_data_list:
                        prayer_type = prayer_data.get('prayer_type', '').lower()
                        prayer_status = prayer_data.get('status', '')
                        is_completed = prayer_data.get('completed', False)
                        prayer_time_str = prayer_data.get('prayer_time', '')
                        
                        logger.info(f"Prayer {prayer_type} for {user.email}: status={prayer_status}, completed={is_completed}")
                        
                        # Send reminder only if prayer is in pending state and not completed
                        if prayer_status == 'pending' and not is_completed:
                            # Check if we already sent a reminder for this prayer today
                            existing_notification = PrayerNotification.query.filter_by(
                                user_id=user.id,
                                prayer_type=prayer_type,
                                prayer_date=now_user_tz.date(),
                                notification_type='reminder'
                            ).first()
                            
                            if not existing_notification:
                                # Parse prayer time for the reminder
                                prayer_time = datetime.strptime(prayer_time_str, '%H:%M').time()
                                prayer_datetime = datetime.combine(now_user_tz.date(), prayer_time)
                                prayer_datetime = user_tz.localize(prayer_datetime)
                                
                                logger.info(f"Sending reminder for pending prayer {prayer_type} to {user.email}")
                                
                                # Send reminder
                                notification_service = NotificationService(config)
                                result = notification_service.send_prayer_reminder(
                                    user, prayer_type, prayer_datetime
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
                            else:
                                logger.info(f"Reminder already sent for {prayer_type} to {user.email}")
                        else:
                            logger.info(f"Skipping {prayer_type} for {user.email} - status: {prayer_status}, completed: {is_completed}")
                
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


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_prayer_window_reminders')
def send_prayer_window_reminders(self):
    """
    Send reminders during prayer time windows if prayers haven't been completed.
    This task runs every 5 minutes to check for prayers that are in their completion window.
    """
    with app.app_context():
        try:
            logger.info("Starting prayer window reminders task")
            # Get current time in UTC
            now_utc = datetime.utcnow()
            logger.info(f"Current UTC time: {now_utc}")
            
            # Get all users with email notifications enabled
            users = User.query.filter_by(
                email_notifications=True,
                notification_enabled=True,
                email_verified=True
            ).all()
            
            logger.info(f"Found {len(users)} eligible users for window reminders")
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
                    prayer_times = prayer_times_result.get('prayers', []) if prayer_times_result.get('success') else []
                    
                    if not prayer_times:
                        continue
                    
                    # Check each prayer for window reminders
                    for prayer_data in prayer_times:
                        prayer_type = prayer_data.get('prayer_type', '').lower()
                        prayer_time_str = prayer_data.get('prayer_time', '')
                        is_completed = prayer_data.get('completed', False)
                        time_status = prayer_data.get('time_status', 'unknown')
                        
                        # Only send reminders for prayers that are in their time window and not completed
                        if time_status == 'during' and not is_completed:
                            # Check if we already sent a window reminder for this prayer today
                            existing_notification = PrayerNotification.query.filter_by(
                                user_id=user.id,
                                prayer_type=prayer_type,
                                prayer_date=now_user_tz.date(),
                                notification_type='window_reminder'
                            ).first()
                            
                            if not existing_notification:
                                # Parse prayer time
                                prayer_time = datetime.strptime(prayer_time_str, '%H:%M').time()
                                prayer_datetime = datetime.combine(now_user_tz.date(), prayer_time)
                                prayer_datetime = user_tz.localize(prayer_datetime)
                                
                                # Send window reminder
                                notification_service = NotificationService(config)
                                result = notification_service.send_prayer_window_reminder(
                                    user, prayer_type, prayer_datetime, prayer_data
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
                                    logger.error(f"Failed to send window reminder to {user.email}: {result.get('error')}")
                
                except Exception as e:
                    total_errors += 1
                    logger.error(f"Error processing user {user.email}: {str(e)}")
                    continue
            
            result = {
                'status': 'completed',
                'window_reminders_sent': total_reminders_sent,
                'errors': total_errors,
                'total_users_processed': len(users),
                'timestamp': now_utc.isoformat()
            }
            logger.info(f"Prayer window reminders task completed: {result}")
            return result
            
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
