"""Email verification tasks for Celery.

This module contains Celery tasks for checking unverified emails
and sending verification reminders to users who haven't verified their email addresses.
"""

from datetime import datetime, timedelta

from celery import current_task

from app.config.settings import get_config
from app.models.email_verification import EmailVerification
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from config.celery_config import celery_app
from config.database import db
from config.logging_config import get_logger
from main import app

logger = get_logger(__name__)


@celery_app.task(bind=True, name='app.tasks.email_verification.check_and_send_verification_reminders')
def check_and_send_verification_reminders(_self):
    """Check all users with unverified emails and send verification reminders.

    This task:
    1. Finds all users with email_verified=False
    2. Checks if they have recent verification attempts (to avoid spam)
    3. Sends new verification emails to eligible users
    4. Logs the results for monitoring

    This task should run periodically (e.g., daily) to remind users to verify their emails.
    """
    with app.app_context():
        try:
            logger.info("Starting email verification reminder task")

            # Get configuration
            config = get_config()
            EmailService(config)
            auth_service = AuthService(config)

            # Find all users with unverified emails
            unverified_users = User.query.filter_by(email_verified=False).all()

            logger.info(f"Found {len(unverified_users)} users with unverified emails")

            if not unverified_users:
                logger.info("No users with unverified emails found")
                return {
                    'status': 'completed',
                    'message': 'No unverified users found',
                    'total_users': 0,
                    'emails_sent': 0,
                    'skipped': 0,
                    'errors': 0
                }

            # Track results
            emails_sent = 0
            skipped = 0
            errors = 0
            results = []

            # Check each user
            for user in unverified_users:
                try:
                    logger.info(f"Processing user: {user.email} (ID: {user.id})")

                    # Check if user has a recent verification attempt (within last 24 hours)
                    recent_verification = EmailVerification.query.filter_by(
                        user_id=user.id,
                        verification_type='email_verification',
                        is_used=False
                    ).filter(
                        EmailVerification.created_at >= datetime.utcnow() - timedelta(hours=24)
                    ).first()

                    if recent_verification:
                        logger.info(f"Skipping {user.email} - recent verification attempt exists")
                        skipped += 1
                        results.append({
                            'user_id': user.id,
                            'email': user.email,
                            'status': 'skipped',
                            'reason': 'Recent verification attempt exists'
                        })
                        continue

                    # Check if user has too many failed attempts (more than 5 in last 7 days)
                    failed_attempts = EmailVerification.query.filter_by(
                        user_id=user.id,
                        verification_type='email_verification',
                        is_used=True
                    ).filter(
                        EmailVerification.created_at >= datetime.utcnow() - timedelta(days=7)
                    ).count()

                    if failed_attempts >= 5:
                        logger.info(f"Skipping {user.email} - too many failed attempts ({failed_attempts})")
                        skipped += 1
                        results.append({
                            'user_id': user.id,
                            'email': user.email,
                            'status': 'skipped',
                            'reason': f'Too many failed attempts ({failed_attempts})'
                        })
                        continue

                    # Send verification email
                    logger.info(f"Sending verification email to {user.email}")
                    result = auth_service.send_email_verification(user.id)

                    if result.get('success'):
                        emails_sent += 1
                        logger.info(f"Successfully sent verification email to {user.email}")
                        results.append({
                            'user_id': user.id,
                            'email': user.email,
                            'status': 'sent',
                            'verification_id': result.get('verification_id')
                        })
                    else:
                        errors += 1
                        logger.error(f"Failed to send verification email to {user.email}: {result.get('error')}")
                        results.append({
                            'user_id': user.id,
                            'email': user.email,
                            'status': 'error',
                            'error': result.get('error')
                        })

                except Exception as e:
                    errors += 1
                    logger.error(f"Error processing user {user.email}: {e!s}")
                    results.append({
                        'user_id': user.id,
                        'email': user.email,
                        'status': 'error',
                        'error': str(e)
                    })

            # Log summary
            summary = {
                'status': 'completed',
                'message': 'Email verification reminder task completed',
                'total_users': len(unverified_users),
                'emails_sent': emails_sent,
                'skipped': skipped,
                'errors': errors,
                'results': results
            }

            logger.info(f"Email verification reminder task completed: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error in email verification reminder task: {e!s}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.email_verification.send_verification_to_user')
def send_verification_to_user(self, user_id: int):
    """Send email verification to a specific user.

    Args:
        self: Celery task instance.
        user_id: ID of the user to send verification to

    Returns:
        Dict[str, Any]: Result with success status or error
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'user_id': user_id})
            logger.info(f"Sending email verification to user ID: {user_id}")

            # Get user
            user = User.query.get(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            if user.email_verified:
                return {
                    'success': False,
                    'error': 'Email is already verified'
                }

            # Get configuration and services
            config = get_config()
            auth_service = AuthService(config)

            # Send verification email
            result = auth_service.send_email_verification(user_id)

            if result.get('success'):
                logger.info(f"Successfully sent verification email to {user.email}")
                return {
                    'success': True,
                    'message': f'Verification email sent to {user.email}',
                    'user_id': user_id,
                    'email': user.email,
                    'verification_id': result.get('verification_id')
                }
            logger.error(f"Failed to send verification email to {user.email}: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'user_id': user_id,
                'email': user.email
            }

        except Exception as e:
            logger.error(f"Error sending verification email to user {user_id}: {e!s}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e), 'user_id': user_id}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.email_verification.cleanup_expired_verifications')
def cleanup_expired_verifications(self):
    """Clean up expired email verification codes.

    This task removes verification codes that have expired and are no longer valid.
    This helps keep the database clean and prevents confusion.
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'task': 'cleanup_expired_verifications'})
            logger.info("Starting cleanup of expired email verifications")

            # Find expired verification codes
            expired_verifications = EmailVerification.query.filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).all()

            logger.info(f"Found {len(expired_verifications)} expired verification codes")

            if not expired_verifications:
                logger.info("No expired verification codes found")
                return {
                    'status': 'completed',
                    'message': 'No expired verifications found',
                    'deleted_count': 0
                }

            # Delete expired verifications
            deleted_count = 0
            for verification in expired_verifications:
                try:
                    db.session.delete(verification)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting verification {verification.id}: {e!s}")

            # Commit changes
            db.session.commit()

            result = {
                'status': 'completed',
                'message': 'Cleanup completed successfully',
                'deleted_count': deleted_count,
                'total_found': len(expired_verifications)
            }

            logger.info(f"Expired verification cleanup completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in expired verification cleanup task: {e!s}")
            db.session.rollback()
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise


@celery_app.task(bind=True, name='app.tasks.email_verification.get_verification_stats')
def get_verification_stats(self):
    """Get statistics about email verification status.

    Returns:
        Dict[str, Any]: Statistics about verified/unverified users and verification attempts
    """
    with app.app_context():
        try:
            # Update task state
            self.update_state(state='PROGRESS', meta={'task': 'get_verification_stats'})
            logger.info("Getting email verification statistics")

            # Get user statistics
            total_users = User.query.count()
            verified_users = User.query.filter_by(email_verified=True).count()
            unverified_users = User.query.filter_by(email_verified=False).count()

            # Get verification attempt statistics
            total_verifications = EmailVerification.query.filter_by(
                verification_type='email_verification'
            ).count()

            used_verifications = EmailVerification.query.filter_by(
                verification_type='email_verification',
                is_used=True
            ).count()

            pending_verifications = EmailVerification.query.filter_by(
                verification_type='email_verification',
                is_used=False
            ).count()

            expired_verifications = EmailVerification.query.filter(
                EmailVerification.verification_type == 'email_verification',
                EmailVerification.expires_at < datetime.utcnow()
            ).count()

            # Get recent verification attempts (last 7 days)
            recent_attempts = EmailVerification.query.filter(
                EmailVerification.verification_type == 'email_verification',
                EmailVerification.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()

            stats = {
                'status': 'completed',
                'message': 'Email verification statistics retrieved',
                'user_stats': {
                    'total_users': total_users,
                    'verified_users': verified_users,
                    'unverified_users': unverified_users,
                    'verification_rate': round((verified_users / total_users * 100), 2) if total_users > 0 else 0
                },
                'verification_stats': {
                    'total_verifications': total_verifications,
                    'used_verifications': used_verifications,
                    'pending_verifications': pending_verifications,
                    'expired_verifications': expired_verifications,
                    'recent_attempts_7_days': recent_attempts
                }
            }

            logger.info(f"Email verification statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting verification statistics: {e!s}")
            current_task.update_state(
                state='FAILURE',
                meta={'error': str(e)}
            )
            raise
