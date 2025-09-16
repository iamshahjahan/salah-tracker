"""Prayer Notifications API routes.

This module defines API endpoints for managing prayer notifications,
including completion links and notification preferences.
"""


from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.notification_service import NotificationService

# Create blueprint
notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/complete-prayer/<completion_link_id>', methods=['GET'])
def show_complete_prayer_page(completion_link_id):
    """Show prayer completion confirmation page."""
    try:
        from app.models.prayer_notification import PrayerNotification
        from app.models.user import User

        # Find the notification
        notification = PrayerNotification.query.filter_by(completion_link_id=completion_link_id).first()

        if not notification:
            return render_template('prayer_completion_error.html',
                                 error="Invalid or expired completion link"), 404

        # Check if already completed
        if notification.completed_via_link:
            # Get the completion time from the PrayerCompletion record
            from app.models.prayer import Prayer, PrayerCompletion
            prayer = Prayer.query.filter_by(
                user_id=notification.user_id,
                prayer_type=notification.prayer_type,
                prayer_date=notification.prayer_date
            ).first()

            completed_at = None
            if prayer:
                completion = PrayerCompletion.query.filter_by(
                    user_id=notification.user_id,
                    prayer_id=prayer.id
                ).first()
                if completion:
                    completed_at = completion.marked_at

            return render_template('prayer_completion_success.html',
                                 message="Prayer already completed!",
                                 prayer_type=notification.prayer_type,
                                 completed_at=completed_at)

        # Check if link is expired (2 hours after creation)
        from datetime import datetime, timedelta
        if notification.created_at and datetime.utcnow() > notification.created_at + timedelta(hours=2):
            return render_template('prayer_completion_error.html',
                                 error="This completion link has expired"), 400

        # Get user info
        user = User.query.get(notification.user_id)

        return render_template('prayer_completion.html',
                             completion_link_id=completion_link_id,
                             prayer_type=notification.prayer_type,
                             prayer_date=notification.prayer_date,
                             user_name=user.first_name or user.username)

    except Exception:
        return render_template('prayer_completion_error.html',
                             error="An error occurred processing your request"), 500


@notifications_bp.route('/complete-prayer/<completion_link_id>', methods=['POST'])
def complete_prayer_via_link(completion_link_id):
    """Mark a prayer as completed via completion link."""
    try:
        notification_service = NotificationService()
        result = notification_service.mark_prayer_completed_via_link(completion_link_id)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get notification preferences for the current user."""
    try:
        user_id = get_jwt_identity()

        from app.models.user import User
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'preferences': {
                'email_notifications': user.email_notifications,
                'reminder_times': user.reminder_times,
                'notification_enabled': user.notification_enabled
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """Update notification preferences for the current user."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        from app.models.user import User
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update preferences
        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']

        if 'reminder_times' in data:
            user.reminder_times = data['reminder_times']

        if 'notification_enabled' in data:
            user.notification_enabled = data['notification_enabled']

        from config.database import db
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'preferences': {
                'email_notifications': user.email_notifications,
                'reminder_times': user.reminder_times,
                'notification_enabled': user.notification_enabled
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/test-reminder', methods=['POST'])
@jwt_required()
def test_prayer_reminder():
    """Send a test prayer reminder to the current user."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        from datetime import datetime, timedelta

        from app.models.user import User

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        prayer_type = data.get('prayer_type', 'dhuhr')
        # Set prayer time to 5 minutes from now for testing
        prayer_time = datetime.utcnow() + timedelta(minutes=5)

        notification_service = NotificationService()
        result = notification_service.send_prayer_reminder(user, prayer_type, prayer_time)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/consistency-nudge', methods=['POST'])
@jwt_required()
def send_consistency_nudge():
    """Send a consistency nudge to the current user."""
    try:
        user_id = get_jwt_identity()

        from app.models.user import User
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        notification_service = NotificationService()
        result = notification_service.send_consistency_nudge(user)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
