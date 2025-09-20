"""Prayer reminder tasks for Celery.

This module contains Celery tasks for sending prayer reminders,
managing notification schedules, and handling prayer-related background jobs.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pytz
from celery import current_task

from app.config.settings import get_config
from app.models.prayer_notification import PrayerNotification
from app.models.user import User
from app.services.notification_service import NotificationService
from app.services.prayer_service import PrayerService
from config.celery_config import celery_app
from config.database import db
from config.logging_config import get_logger
from main import app

logger = get_logger(__name__)

# Constants
DEFAULT_TIMEZONE = 'UTC'
MAX_TEST_USERS = 5
DEFAULT_CLEANUP_DAYS = 30


# Helper functions for prayer reminders
def _get_eligible_users() -> List[User]:
    """Get all users eligible for prayer reminders.

    Returns:
        List of users with email notifications enabled and verified emails.
    """
    return User.query.filter_by(
        email_notifications=True,
        notification_enabled=True,
        email_verified=True
    ).all()


def _get_user_prayer_data(user: User, current_time: datetime) -> Optional[List[Dict[str, Any]]]:
    """Get prayer data for a specific user.

    Args:
        user: User object
        current_time: Current time in user's timezone

    Returns:
        List of prayer data or None if not found
    """
    try:
        config = get_config()
        prayer_service = PrayerService(config)

        prayer_times_result = prayer_service.get_prayer_times(
            user.id,
            current_time.date().strftime('%Y-%m-%d'),
            current_time
        )

        if prayer_times_result.get('success'):
            return prayer_times_result.get('prayers', [])

        logger.warning(f"Failed to get prayer times for user {user.email}")
        return None

    except Exception as e:
        logger.error(f"Error getting prayer data for user {user.email}: {e}")
        return None


def _should_send_reminder(prayer_data: Dict[str, Any]) -> bool:
    """Check if a reminder should be sent for a prayer.

    Args:
        prayer_data: Prayer data dictionary

    Returns:
        True if reminder should be sent, False otherwise
    """
    prayer_status = prayer_data.get('prayer_status', '')
    is_completed = prayer_data.get('completed', False)

    return prayer_status == 'ongoing' and not is_completed


def _has_existing_notification(user_id: int, prayer_type: str, prayer_date: datetime.date) -> bool:
    """Check if a notification already exists for this prayer today.

    Args:
        user_id: User ID
        prayer_type: Type of prayer
        prayer_date: Date of the prayer

    Returns:
        True if notification exists, False otherwise
    """
    existing_notification = PrayerNotification.query.filter_by(
        user_id=user_id,
        prayer_type=prayer_type,
        prayer_date=prayer_date,
        notification_type='reminder'
    ).first()

    return existing_notification is not None


def _parse_prayer_datetime(prayer_time_str: str, prayer_date: datetime.date, user_tz: pytz.BaseTzInfo) -> datetime:
    """Parse prayer time string and create localized datetime.

    Args:
        prayer_time_str: Prayer time in HH:MM format
        prayer_date: Date of the prayer
        user_tz: User's timezone

    Returns:
        Localized prayer datetime
    """
    try:
        prayer_time = datetime.strptime(prayer_time_str, '%H:%M').time()
        prayer_datetime = datetime.combine(prayer_date, prayer_time)
        return user_tz.localize(prayer_datetime)
    except ValueError as e:
        logger.error(f"Error parsing prayer time '{prayer_time_str}': {e}")
        raise


def _send_prayer_reminder(config: Any, user: User, prayer_type: str, prayer_datetime: datetime) -> bool:
    """Send a prayer reminder to a user.

    Args:
        config: Application configuration
        user: User object
        prayer_type: Type of prayer
        prayer_datetime: Prayer datetime

    Returns:
        True if reminder sent successfully, False otherwise
    """
    try:
        notification_service = NotificationService(config)
        result = notification_service.send_prayer_reminder(
            user, prayer_type, prayer_datetime
        )

        if result.get('success'):
            logger.info(f"Reminder sent successfully for {prayer_type} to {user.email}")
            return True
        logger.error(f"Failed to send reminder to {user.email}: {result.get('error')}")
        return False

    except Exception as e:
        logger.error(f"Exception sending reminder to {user.email}: {e}")
        return False


def _send_user_reminders(config: Any, user: User, prayer_data_list: List[Dict[str, Any]],
                        now_user_tz: datetime, user_tz: pytz.BaseTzInfo) -> Tuple[int, int]:
    """Send reminders for all eligible prayers for a user.

    Args:
        config: Application configuration
        user: User object
        prayer_data_list: List of prayer data
        now_user_tz: Current time in user timezone
        user_tz: User's timezone object

    Returns:
        Tuple of (errors_count, reminders_sent_count)
    """
    total_errors = 0
    total_reminders_sent = 0

    for prayer_data in prayer_data_list:
        try:
            prayer_type = prayer_data.get('prayer_type', '').lower()
            prayer_time_str = prayer_data.get('prayer_time', '')

            logger.debug(f"Processing prayer {prayer_type} for {user.email}: "
                        f"status={prayer_data.get('status')}, completed={prayer_data.get('completed')}")

            # Check if reminder should be sent
            if not _should_send_reminder(prayer_data):
                logger.debug(f"Skipping {prayer_type} for {user.email} - not eligible for reminder")
                continue

            # Check if reminder already sent today
            if _has_existing_notification(user.id, prayer_type, now_user_tz.date()):
                logger.debug(f"Reminder already sent for {prayer_type} to {user.email}")
                continue

            # Parse prayer datetime
            prayer_datetime = _parse_prayer_datetime(prayer_time_str, now_user_tz.date(), user_tz)

            # Send reminder
            logger.info(f"Sending reminder for {prayer_type} to {user.email}")
            if _send_prayer_reminder(config, user, prayer_type, prayer_datetime):
                total_reminders_sent += 1
            else:
                total_errors += 1

        except Exception as e:
            logger.error(f"Error processing prayer {prayer_data.get('prayer_type', 'unknown')} for {user.email}: {e}")
            total_errors += 1
            continue

    return total_reminders_sent, total_errors


def _process_user_reminders(user: User, now_utc: datetime) -> Tuple[int, int]:
    """Process prayer reminders for a single user.

    Args:
        user: User object
        now_utc: Current UTC time

    Returns:
        Tuple of (reminders_sent_count, errors_count)
    """
    try:
        logger.info(f"Processing user: {user.email} (ID: {user.id})")

        # Get user's timezone and current time
        user_tz = pytz.timezone(user.timezone or DEFAULT_TIMEZONE)
        now_user_tz = now_utc.replace(tzinfo=pytz.UTC).astimezone(user_tz)

        logger.debug(f"User timezone: {user.timezone}, Current user time: {now_user_tz}")

        # Get prayer data
        prayer_data_list = _get_user_prayer_data(user, now_user_tz)
        if not prayer_data_list:
            logger.info(f"No prayer data found for {user.email}")
            return 0, 0

        # Send reminders for eligible prayers
        config = get_config()
        return _send_user_reminders(config, user, prayer_data_list, now_user_tz, user_tz)

    except Exception as e:
        logger.error(f"Error processing user {user.email}: {e}")
        return 0, 1


def _create_task_result(reminders_sent: int, errors: int, users_processed: int, timestamp: datetime) -> Dict[str, Any]:
    """Create standardized task result dictionary.

    Args:
        reminders_sent: Number of reminders sent
        errors: Number of errors encountered
        users_processed: Number of users processed
        timestamp: Task execution timestamp

    Returns:
        Standardized result dictionary
    """
    return {
        'status': 'completed',
        'reminders_sent': reminders_sent,
        'errors': errors,
        'total_users_processed': users_processed,
        'timestamp': timestamp.isoformat()
    }


# Main Celery tasks
@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_prayer_reminders')
def send_prayer_reminders(self) -> Dict[str, Any]:
    """Send prayer reminders to users for prayers in pending state.

    This task runs every 5 minutes and checks for users who have
    prayers in pending state (during prayer time) that are not completed.

    Returns:
        Dict containing task execution results
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'task': 'send_prayer_reminders'})
            logger.info("Starting prayer reminders task")

            now_utc = datetime.utcnow()
            logger.info(f"Current UTC time: {now_utc}")

            # Get eligible users
            users = _get_eligible_users()
            logger.info(f"Found {len(users)} eligible users for reminders")

            if not users:
                logger.info("No eligible users found for reminders")
                return _create_task_result(0, 0, 0, now_utc)

            # Process each user
            total_reminders_sent = 0
            total_errors = 0

            for i, user in enumerate(users, 1):
                reminders, errors = _process_user_reminders(user, now_utc)
                total_errors += errors
                total_reminders_sent += reminders

                # Update task progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current_user': user.email,
                        'reminders_sent': total_reminders_sent,
                        'errors': total_errors,
                        'processed': i,
                        'total': len(users)
                    }
                )

            result = _create_task_result(total_reminders_sent, total_errors, len(users), now_utc)
            logger.info(f"Prayer reminders task completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Fatal error in prayer reminders task: {e}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.send_individual_reminder')
def send_individual_reminder(self, user_id: int, prayer_type: str, prayer_time: str) -> Dict[str, Any]:
    """Send a prayer reminder to a specific user for a specific prayer.

    Args:
        self: Celery task instance.
        user_id: ID of the user to send reminder to
        prayer_type: Type of prayer (fajr, dhuhr, asr, maghrib, isha)
        prayer_time: Time of the prayer in HH:MM format

    Returns:
        Dict containing task execution results
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(
                state='PROGRESS',
                meta={'user_id': user_id, 'prayer_type': prayer_type, 'prayer_time': prayer_time}
            )
            logger.info(f"Starting individual reminder task for user {user_id}, prayer {prayer_type} at {prayer_time}")

            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return {'status': 'error', 'message': 'User not found'}

            logger.info(f"Found user: {user.email} (ID: {user_id})")

            # Parse prayer time and create datetime
            user_tz = pytz.timezone(user.timezone or DEFAULT_TIMEZONE)
            prayer_datetime = _parse_prayer_datetime(prayer_time, datetime.utcnow().date(), user_tz)

            logger.info(f"Prayer datetime: {prayer_datetime}")

            # Send reminder
            logger.info(f"Sending reminder to {user.email} for {prayer_type}")
            config = get_config()

            success = _send_prayer_reminder(config, user, prayer_type, prayer_datetime)

            result = {
                'status': 'completed' if success else 'failed',
                'user_id': user_id,
                'prayer_type': prayer_type,
                'success': success
            }

            logger.info(f"Individual reminder result for {user.email}: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in individual reminder task for user {user_id}: {e}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.cleanup_old_notifications')
def cleanup_old_notifications(self, days_old: int = DEFAULT_CLEANUP_DAYS) -> Dict[str, Any]:
    """Clean up old prayer notifications to keep the database clean.

    Args:
        self: Celery task instance.
        days_old: Number of days old notifications to delete (default: 30)

    Returns:
        Dict containing cleanup results
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'days_old': days_old})
            logger.info(f"Starting cleanup of old notifications older than {days_old} days")

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            logger.info(f"Cutoff date: {cutoff_date}")

            # Count notifications to be deleted first
            count_to_delete = PrayerNotification.query.filter(
                PrayerNotification.created_at < cutoff_date
            ).count()
            logger.info(f"Found {count_to_delete} notifications to delete")

            if count_to_delete == 0:
                logger.info("No old notifications found to delete")
                return {
                    'status': 'completed',
                    'deleted_count': 0,
                    'cutoff_date': cutoff_date.isoformat()
                }

            # Delete old notifications
            deleted_count = PrayerNotification.query.filter(
                PrayerNotification.created_at < cutoff_date
            ).delete()

            logger.info(f"Deleted {deleted_count} old notifications")
            db.session.commit()

            result = {
                'status': 'completed',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            logger.info(f"Cleanup task completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            db.session.rollback()
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.prayer_reminders.test_reminder_system')
def test_reminder_system(self) -> Dict[str, Any]:
    """Test the reminder system by sending a test reminder to all users.

    This is useful for testing the email system and notification flow.

    Returns:
        Dict containing test results
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'task': 'test_reminder_system'})
            logger.info("Starting test reminder system task")

            # Limit to a few users for testing
            users = User.query.filter_by().limit(MAX_TEST_USERS).all()
            logger.info(f"Found {len(users)} users for testing")

            if not users:
                logger.warning("No users found for testing")
                return {
                    'status': 'completed',
                    'test_type': 'reminder_system',
                    'users_tested': 0,
                    'results': []
                }

            results = []

            for user in users:
                try:
                    logger.info(f"Testing reminder for user {user.email} (ID: {user.id})")

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

                    logger.info(f"Test reminder queued for {user.email}, task ID: {result.id}")

                except Exception as e:
                    logger.error(f"Failed to queue test reminder for {user.email}: {e}")
                    results.append({
                        'user_id': user.id,
                        'user_email': user.email,
                        'status': 'failed',
                        'error': str(e)
                    })

            result = {
                'status': 'completed',
                'test_type': 'reminder_system',
                'users_tested': len(users),
                'results': results
            }
            logger.info(f"Test reminder system task completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in test reminder system task: {e}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise
