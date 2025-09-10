"""
Notification service for managing prayer reminders and notifications.

This service handles email notifications, prayer reminders, and notification
preferences with proper scheduling and delivery management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from flask_mail import Message

from .base_service import BaseService
from app.models.user import User
from app.models.prayer import Prayer
from app.config.settings import Config


class NotificationService(BaseService):
    """
    Service for managing notifications and reminders.
    
    This service provides methods for sending email notifications, managing
    prayer reminders, and handling notification preferences.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the notification service.
        
        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        self.mail_config = self.config.MAIL_CONFIG
    
    def send_prayer_reminder(self, user_id: int, prayer_id: int) -> Dict[str, Any]:
        """
        Send prayer reminder notification to user.
        
        Args:
            user_id: ID of the user to send reminder to.
            prayer_id: ID of the prayer to remind about.
            
        Returns:
            Dict[str, Any]: Notification result with success status or error.
        """
        try:
            if not self.mail_config:
                return {
                    'success': False,
                    'error': 'Email service not configured'
                }
            
            # Get user and prayer
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            prayer = self.get_record_by_id(Prayer, prayer_id)
            if not prayer:
                return {
                    'success': False,
                    'error': 'Prayer not found'
                }
            
            # Check if user has notifications enabled
            if not user.notification_enabled:
                return {
                    'success': False,
                    'error': 'User has notifications disabled'
                }
            
            # Send email notification
            success = self._send_prayer_reminder_email(user, prayer)
            
            if success:
                self.logger.info(f"Prayer reminder sent to {user.email} for {prayer.name}")
                return {
                    'success': True,
                    'message': 'Prayer reminder sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send prayer reminder'
                }
            
        except Exception as e:
            return self.handle_service_error(e, 'send_prayer_reminder')
    
    def send_welcome_email(self, user_id: int) -> Dict[str, Any]:
        """
        Send welcome email to newly registered user.
        
        Args:
            user_id: ID of the newly registered user.
            
        Returns:
            Dict[str, Any]: Email result with success status or error.
        """
        try:
            if not self.mail_config:
                return {
                    'success': False,
                    'error': 'Email service not configured'
                }
            
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Send welcome email
            success = self._send_welcome_email(user)
            
            if success:
                self.logger.info(f"Welcome email sent to {user.email}")
                return {
                    'success': True,
                    'message': 'Welcome email sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send welcome email'
                }
            
        except Exception as e:
            return self.handle_service_error(e, 'send_welcome_email')
    
    def send_daily_summary(self, user_id: int, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Send daily prayer summary to user.
        
        Args:
            user_id: ID of the user to send summary to.
            date: Date string in YYYY-MM-DD format. If None, uses yesterday.
            
        Returns:
            Dict[str, Any]: Summary result with success status or error.
        """
        try:
            if not self.mail_config:
                return {
                    'success': False,
                    'error': 'Email service not configured'
                }
            
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Check if user has notifications enabled
            if not user.notification_enabled:
                return {
                    'success': False,
                    'error': 'User has notifications disabled'
                }
            
            # Parse date
            if date:
                try:
                    target_date = datetime.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid date format. Use YYYY-MM-DD'
                    }
            else:
                target_date = (datetime.now() - timedelta(days=1)).date()
            
            # Get prayer data for the date
            prayer_data = self._get_daily_prayer_data(user, target_date)
            
            # Send daily summary email
            success = self._send_daily_summary_email(user, target_date, prayer_data)
            
            if success:
                self.logger.info(f"Daily summary sent to {user.email} for {target_date}")
                return {
                    'success': True,
                    'message': 'Daily summary sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to send daily summary'
                }
            
        except Exception as e:
            return self.handle_service_error(e, 'send_daily_summary')
    
    def update_notification_preferences(self, user_id: int, enabled: bool) -> Dict[str, Any]:
        """
        Update user notification preferences.
        
        Args:
            user_id: ID of the user.
            enabled: Whether notifications should be enabled.
            
        Returns:
            Dict[str, Any]: Update result with success status or error.
        """
        try:
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Update notification preference
            self.update_record(user, notification_enabled=enabled)
            
            self.logger.info(f"Notification preferences updated for {user.email}: {enabled}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': f'Notifications {"enabled" if enabled else "disabled"} successfully'
            }
            
        except Exception as e:
            return self.handle_service_error(e, 'update_notification_preferences')
    
    def _send_prayer_reminder_email(self, user: User, prayer: Prayer) -> bool:
        """
        Send prayer reminder email to user.
        
        Args:
            user: User instance.
            prayer: Prayer instance.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            from mail_config import mail
            
            subject = f"Prayer Reminder - {prayer.name}"
            body = f"""
            Assalamu Alaikum {user.first_name},
            
            This is a reminder that {prayer.name} prayer time is approaching.
            
            Prayer Time: {prayer.prayer_time.strftime('%H:%M')}
            Date: {prayer.prayer_date.strftime('%B %d, %Y')}
            
            May Allah accept your prayers.
            
            Best regards,
            Salah Reminders Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending prayer reminder email: {str(e)}")
            return False
    
    def _send_welcome_email(self, user: User) -> bool:
        """
        Send welcome email to newly registered user.
        
        Args:
            user: User instance.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            from mail_config import mail
            
            subject = "Welcome to Salah Reminders!"
            body = f"""
            Assalamu Alaikum {user.first_name},
            
            Welcome to Salah Reminders! We're excited to help you maintain consistency in your daily prayers.
            
            Your account has been created successfully with the following details:
            - Name: {user.first_name} {user.last_name}
            - Email: {user.email}
            - Location: {user.location_lat}, {user.location_lng}
            - Timezone: {user.timezone}
            
            You can now:
            - Track your daily prayers
            - Mark missed prayers as Qada
            - View your prayer statistics
            - Set up prayer reminders
            
            If you have any questions or need assistance, please don't hesitate to contact us.
            
            May Allah bless you and accept your prayers.
            
            Best regards,
            Salah Reminders Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    def _send_daily_summary_email(self, user: User, date: datetime.date, 
                                 prayer_data: Dict[str, Any]) -> bool:
        """
        Send daily prayer summary email to user.
        
        Args:
            user: User instance.
            date: Date of the summary.
            prayer_data: Prayer completion data for the date.
            
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        try:
            from mail_config import mail
            
            # Calculate summary statistics
            total_prayers = prayer_data.get('total_prayers', 0)
            completed_prayers = prayer_data.get('completed_prayers', 0)
            completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
            
            subject = f"Daily Prayer Summary - {date.strftime('%B %d, %Y')}"
            body = f"""
            Assalamu Alaikum {user.first_name},
            
            Here's your prayer summary for {date.strftime('%B %d, %Y')}:
            
            📊 Daily Statistics:
            - Total Prayers: {total_prayers}
            - Completed Prayers: {completed_prayers}
            - Completion Rate: {completion_rate:.1f}%
            
            🕌 Prayer Details:
            """
            
            # Add prayer details
            for prayer in prayer_data.get('prayers', []):
                status = "✅ Completed" if prayer.get('completed') else "❌ Missed"
                if prayer.get('completion', {}).get('is_qada'):
                    status = "🔄 Qada"
                elif prayer.get('completion', {}).get('is_late'):
                    status = "⏰ Late"
                
                body += f"- {prayer.get('name', 'Unknown')} ({prayer.get('time', 'N/A')}): {status}\n"
            
            body += f"""
            
            Keep up the great work! Consistency in prayer is a blessing from Allah.
            
            May Allah accept your prayers and grant you success in this world and the next.
            
            Best regards,
            Salah Reminders Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending daily summary email: {str(e)}")
            return False
    
    def _get_daily_prayer_data(self, user: User, date: datetime.date) -> Dict[str, Any]:
        """
        Get prayer data for a specific date.
        
        Args:
            user: User instance.
            date: Date to get prayer data for.
            
        Returns:
            Dict[str, Any]: Prayer data for the date.
        """
        try:
            from app.models.prayer import PrayerCompletion
            
            # Get prayers for the date
            prayers = Prayer.query.filter(
                Prayer.user_id == user.id,
                Prayer.prayer_date == date
            ).all()
            
            # Get completions
            prayer_ids = [prayer.id for prayer in prayers]
            completions = PrayerCompletion.query.filter(
                PrayerCompletion.prayer_id.in_(prayer_ids)
            ).all()
            
            # Group completions by prayer_id
            completions_by_prayer = {c.prayer_id: c for c in completions}
            
            # Build prayer data
            prayer_list = []
            for prayer in prayers:
                completion = completions_by_prayer.get(prayer.id)
                prayer_list.append({
                    'name': prayer.name,
                    'time': prayer.prayer_time.strftime('%H:%M'),
                    'completed': completion is not None,
                    'completion': completion.to_dict() if completion else None
                })
            
            return {
                'total_prayers': len(prayers),
                'completed_prayers': len(completions),
                'prayers': prayer_list
            }
            
        except Exception as e:
            self.logger.error(f"Error getting daily prayer data: {str(e)}")
            return {
                'total_prayers': 0,
                'completed_prayers': 0,
                'prayers': []
            }
