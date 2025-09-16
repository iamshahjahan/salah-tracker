"""Consistency check tasks for Celery.

This module contains Celery tasks for checking user prayer consistency,
sending motivational nudges, and analyzing prayer patterns.
"""


from datetime import date, timedelta

from celery import current_task

from app.models.prayer import PrayerCompletion
from app.models.user import User
from app.services.notification_service import NotificationService
from config.celery_config import celery_app
from main import app


@celery_app.task(bind=True, name='app.tasks.consistency_checks.check_user_consistency')
def check_user_consistency(_self):
    """Check prayer consistency for all users and send motivational nudges.

    to users who have been missing prayers.

    This task runs daily at 10 PM to analyze the day's prayer completion.
    """
    with app.app_context():
        try:
            today = date.today()
            today - timedelta(days=1)

            # Get all users with email notifications enabled
            users = User.query.filter_by(
                email_notifications=True,
                notification_enabled=True,
                email_verified=True
            ).all()

            nudges_sent = 0
            errors = 0

            for user in users:
                try:
                    # Check prayer completion for the last 3 days
                    recent_completions = PrayerCompletion.query.filter(
                        PrayerCompletion.user_id == user.id,
                        PrayerCompletion.prayer_date >= today - timedelta(days=3),
                        PrayerCompletion.is_completed
                    ).all()

                    # Count completed prayers by date
                    completion_by_date = {}
                    for completion in recent_completions:
                        if completion.prayer_date not in completion_by_date:
                            completion_by_date[completion.prayer_date] = 0
                        completion_by_date[completion.prayer_date] += 1

                    # Check if user has been consistently missing prayers
                    total_expected_prayers = 15  # 5 prayers x 3 days
                    total_completed = len(recent_completions)
                    completion_rate = (total_completed / total_expected_prayers) * 100

                    # Send nudge if completion rate is below 60%
                    if completion_rate < 60:
                        notification_service = NotificationService()
                        result = notification_service.send_consistency_nudge(user)

                        if result.get('success'):
                            nudges_sent += 1
                            current_task.update_state(
                                state='PROGRESS',
                                meta={
                                    'current_user': user.email,
                                    'completion_rate': completion_rate,
                                    'nudges_sent': nudges_sent,
                                    'errors': errors
                                }
                            )
                        else:
                            errors += 1
                            print(f"Failed to send nudge to {user.email}: {result.get('error')}")

                except Exception as e:
                    errors += 1
                    print(f"Error checking consistency for user {user.email}: {e!s}")
                    continue

            return {
                'status': 'completed',
                'nudges_sent': nudges_sent,
                'errors': errors,
                'total_users_checked': len(users),
                'check_date': today.isoformat()
            }

        except Exception as e:
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.consistency_checks.analyze_prayer_patterns')
def analyze_prayer_patterns(self, user_id: int, days: int = 30):
    """Analyze prayer patterns for a specific user over a given period.

    Args:
        self: Celery task instance.
        user_id: ID of the user to analyze
        days: Number of days to analyze (default: 30)
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'user_id': user_id, 'days': days})

        user = User.query.get(user_id)
        if not user:
            return {'status': 'error', 'message': 'User not found'}

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get prayer completions for the period
        completions = PrayerCompletion.query.filter(
            PrayerCompletion.user_id == user_id,
            PrayerCompletion.prayer_date >= start_date,
            PrayerCompletion.prayer_date <= end_date,
            PrayerCompletion.is_completed
        ).all()

        # Analyze patterns
        prayer_types = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']
        prayer_stats = {}

        for prayer_type in prayer_types:
            type_completions = [c for c in completions if c.prayer_type.lower() == prayer_type]
            prayer_stats[prayer_type] = {
                'completed': len(type_completions),
                'expected': days,
                'completion_rate': (len(type_completions) / days) * 100
            }

        # Calculate overall statistics
        total_completed = len(completions)
        total_expected = days * 5  # 5 prayers per day
        overall_completion_rate = (total_completed / total_expected) * 100

        # Find most missed prayer
        most_missed = min(prayer_stats.items(), key=lambda x: x[1]['completion_rate'])

        # Find best prayer
        best_prayer = max(prayer_stats.items(), key=lambda x: x[1]['completion_rate'])

        return {
            'status': 'completed',
            'user_id': user_id,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'overall_stats': {
                'total_completed': total_completed,
                'total_expected': total_expected,
                'completion_rate': overall_completion_rate
            },
            'prayer_stats': prayer_stats,
            'insights': {
                'most_missed_prayer': {
                    'prayer': most_missed[0],
                    'completion_rate': most_missed[1]['completion_rate']
                },
                'best_prayer': {
                    'prayer': best_prayer[0],
                    'completion_rate': best_prayer[1]['completion_rate']
                }
            }
        }

    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True, name='app.tasks.consistency_checks.send_weekly_report')
def send_weekly_report(self):
    """Send weekly prayer reports to all users who have opted in for reports.

    This task runs every Sunday at 9 AM.
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'task': 'send_weekly_report'})
        # Get all users with email notifications enabled
        users = User.query.filter_by(
            email_notifications=True,
            notification_enabled=True,
            email_verified=True
        ).all()

        reports_sent = 0
        errors = 0

        for user in users:
            try:
                # Analyze user's prayer patterns for the past week
                result = analyze_prayer_patterns.delay(user.id, 7)

                # Here you could implement a weekly report email template
                # For now, we'll just log the analysis
                print(f"Weekly report generated for user {user.email}: {result.id}")
                reports_sent += 1

            except Exception as e:
                errors += 1
                print(f"Error generating weekly report for user {user.email}: {e!s}")
                continue

        return {
            'status': 'completed',
            'reports_sent': reports_sent,
            'errors': errors,
            'total_users': len(users)
        }

    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True, name='app.tasks.consistency_checks.send_motivational_message')
def send_motivational_message(self, user_id: int, message_type: str = 'general'):
    """Send a motivational message to a specific user.

    Args:
        self: Celery task instance.
        user_id: ID of the user to send message to
        message_type: Type of motivational message (general, streak, comeback)
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'user_id': user_id, 'message_type': message_type})
        user = User.query.get(user_id)
        if not user:
            return {'status': 'error', 'message': 'User not found'}

        if not user.email_notifications:
            return {'status': 'skipped', 'message': 'User has disabled email notifications'}

        # Send motivational nudge
        notification_service = NotificationService()
        result = notification_service.send_consistency_nudge(user)

        return {
            'status': 'completed' if result.get('success') else 'failed',
            'user_id': user_id,
            'message_type': message_type,
            'result': result
        }

    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
