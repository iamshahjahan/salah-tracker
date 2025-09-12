"""
Notification service for managing prayer reminders and notifications.

This service handles sending prayer reminders, completion links,
and managing notification preferences for users.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from flask import current_app, url_for
from flask_mail import Message

from .base_service import BaseService
from .email_service import EmailService
from .email_templates import get_prayer_reminder_template, get_consistency_nudge_template, get_prayer_name_arabic
from app.models.user import User
from app.models.prayer_notification import PrayerNotification
from app.models.inspirational_content import QuranicVerse, Hadith
from app.models.prayer import PrayerCompletion


class NotificationService(BaseService):
    """
    Service for managing prayer notifications and reminders.
    
    This service provides methods for sending prayer reminders,
    managing completion links, and handling notification preferences.
    """
    
    def __init__(self, config=None):
        """Initialize the notification service."""
        super().__init__(config)
        self.email_service = EmailService(config)
    
    def send_prayer_reminder(self, user: User, prayer_type: str, prayer_time: datetime) -> Dict[str, Any]:
        """
        Send a prayer reminder to a user.
        
        Args:
            user: User to send reminder to.
            prayer_type: Type of prayer (fajr, dhuhr, asr, maghrib, isha).
            prayer_time: Time of the prayer.
            
        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            if not user.email_notifications:
                return {
                    'success': False,
                    'error': 'User has disabled email notifications'
                }
            
            # Get inspirational content
            verse = QuranicVerse.get_random_verse('prayer')
            hadith = Hadith.get_random_hadith('prayer')
            
            # Create notification record
            notification = self.create_record(
                PrayerNotification,
                user_id=user.id,
                prayer_type=prayer_type,
                prayer_date=prayer_time.date(),
                notification_type='reminder'
            )
            
            # Generate completion link
            completion_link = notification.get_completion_link(
                current_app.config.get('FRONTEND_URL', 'http://localhost:5001')
            )
            
            # Send email
            if user.language == 'en':
                from app.services.email_templates import get_prayer_name_english
                subject = f"🕌 {get_prayer_name_english(prayer_type)} Prayer Reminder - SalahTracker"
            else:
                from app.services.email_templates import get_prayer_name_arabic
                subject = f"🕌 وقت صلاة {get_prayer_name_arabic(prayer_type)} - SalahTracker"
            
            template = get_prayer_reminder_template(
                user, prayer_type, prayer_time, verse, hadith, completion_link
            )
            
            success = self.email_service._send_email(user.email, subject, template)
            
            if success:
                # Update notification as sent
                notification.sent_at = datetime.utcnow()
                self.db_session.commit()
                
                self.logger.info(f"Prayer reminder sent to {user.email} for {prayer_type}")
                return {
                    'success': True,
                    'message': 'Prayer reminder sent successfully',
                    'notification_id': notification.id
                }
            else:
                print(f"error while sending reminder to: {user.email}")
                return {
                    'success': False,
                    'error': 'Failed to send prayer reminder email'
                }
                
        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'send_prayer_reminder')
    
    def mark_prayer_completed_via_link(self, completion_link_id: str) -> Dict[str, Any]:
        """
        Mark a prayer as completed via completion link.
        
        Args:
            completion_link_id: The completion link ID.
            
        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Find the notification
            notification = PrayerNotification.query.filter_by(
                completion_link_id=completion_link_id
            ).first()
            
            if not notification:
                return {
                    'success': False,
                    'error': 'Invalid completion link'
                }
            
            if not notification.is_completion_link_valid():
                return {
                    'success': False,
                    'error': 'Completion link has expired'
                }
            
            if notification.completed_via_link:
                return {
                    'success': False,
                    'error': 'Prayer already marked as completed via this link'
                }
            
            # Mark prayer as completed
            user = notification.user
            prayer_date = notification.prayer_date
            
            # Find the prayer record for this date and type
            from app.models.prayer import Prayer
            prayer = Prayer.query.filter_by(
                user_id=user.id,
                prayer_type=notification.prayer_type,
                prayer_date=prayer_date
            ).first()
            
            if not prayer:
                return {
                    'success': False,
                    'error': 'Prayer record not found for this date'
                }
            
            # Check if already completed
            existing_completion = PrayerCompletion.query.filter_by(
                user_id=user.id,
                prayer_id=prayer.id
            ).first()
            
            if existing_completion:
                return {
                    'success': False,
                    'error': 'Prayer already marked as completed'
                }
            
            # Create prayer completion record
            self.create_record(
                PrayerCompletion,
                user_id=user.id,
                prayer_id=prayer.id,
                completed_at=datetime.utcnow(),
                is_late=False,
                is_qada=False
            )
            
            # Mark notification as completed via link
            notification.completed_via_link = True
            self.db_session.commit()
            
            self.logger.info(f"Prayer {notification.prayer_type} marked as completed via link for user {user.email}")
            
            return {
                'success': True,
                'message': 'Prayer marked as completed successfully',
                'prayer_type': notification.prayer_type,
                'prayer_date': prayer_date.isoformat()
            }
            
        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'mark_prayer_completed_via_link')
    
    def send_consistency_nudge(self, user: User) -> Dict[str, Any]:
        """
        Send a consistency nudge to a user who has been missing prayers.
        
        Args:
            user: User to send nudge to.
            
        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            if not user.email_notifications:
                return {
                    'success': False,
                    'error': 'User has disabled email notifications'
                }
            
            # Get inspirational content for motivation
            from app.models.inspirational_content import QuranicVerse, Hadith
            verse = QuranicVerse.get_random_verse('patience')
            hadith = Hadith.get_random_hadith('motivation')
            
            subject = "💪 دعنا نعود إلى المسار الصحيح - SalahTracker"
            template = get_consistency_nudge_template(user, verse, hadith)
            
            success = self.email_service._send_email(user.email, subject, template)
            
            if success:
                self.logger.info(f"Consistency nudge sent to {user.email}")
                return {
                    'success': True,
                    'message': 'Consistency nudge sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send consistency nudge email'
                }
                
        except Exception as e:
            return self.handle_service_error(e, 'send_consistency_nudge')
    