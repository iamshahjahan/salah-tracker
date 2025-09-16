"""Prayer routes for managing prayer times, completions, and Qada tracking.

This module provides REST API endpoints for prayer-related operations,
using the modern PrayerService for all business logic.
"""
from datetime import datetime, timedelta
from typing import Any

import pytz
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.config.settings import get_config
from app.models.prayer import PrayerCompletion
from app.models.user import User
from app.services.prayer_service import PrayerService

prayer_bp = Blueprint('prayer', __name__)

@prayer_bp.route('/times', methods=['GET'])
@jwt_required()
def get_prayer_times_for_user():
    """Get prayer times for the current user's location."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use the modern service layer
        config = get_config()
        prayer_service = PrayerService(config)

        # Get date from query parameter or use today
        date_str = request.args.get('date')

        # Get current time in user's timezone
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

        # Get prayer times using the service layer
        result = prayer_service.get_prayer_times(user_id, date_str, current_time)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Unable to fetch prayer times')}), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/times/<date_str>', methods=['GET'])
@jwt_required()
def get_prayer_times_for_date(date_str):
    """Get prayer times for a specific date."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use the modern service layer
        result = get_prayer_times(date_str, user, user_id)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Unable to fetch prayer times')}), 500

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_prayer_times(date_str, user, user_id) -> dict[str, Any]:
    config = get_config()
    prayer_service = PrayerService(config)

    # Get current time in user's timezone
    user_tz = pytz.timezone(user.timezone)
    current_time = datetime.now(user_tz)

    return prayer_service.get_prayer_times(user_id, date_str, current_time)


@prayer_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_prayer():
    """Mark a prayer as completed."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not data or 'prayer_id' not in data:
            return jsonify({'error': 'Prayer ID is required'}), 400

        prayer_id = data['prayer_id']

        # Use the modern service layer
        config = get_config()
        prayer_service = PrayerService(config)
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)
        result = prayer_service.complete_prayer(user_id, prayer_id, current_time)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to complete prayer')}), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/mark-qada', methods=['POST'])
@jwt_required()
def mark_prayer_qada():
    """Mark a prayer as Qada (missed prayer)."""
    try:
        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        if not data or 'prayer_id' not in data:
            return jsonify({'error': 'Prayer ID is required'}), 400

        prayer_id = data['prayer_id']

        # Use the modern service layer
        config = get_config()
        prayer_service = PrayerService(config)
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

        result = prayer_service.mark_prayer_qada(user_id, prayer_id, current_time)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to mark prayer as Qada')}), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/completions', methods=['GET'])
@jwt_required()
def get_prayer_completions():
    """Get prayer completions for the current user."""
    try:
        user_id = get_jwt_identity()

        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        # Use the modern service layer
        config = get_config()
        PrayerService(config)

        # Get completions for the date range
        completions = PrayerCompletion.query.filter(
            PrayerCompletion.user_id == user_id,
            PrayerCompletion.completed_at >= start_date,
            PrayerCompletion.completed_at <= end_date
        ).all()

        return jsonify({
            'completions': [completion.to_dict() for completion in completions]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/status/<date_str>', methods=['GET'])
@jwt_required()
def get_prayer_status_for_date(date_str):
    """Get prayer status for a specific date."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use the modern service layer
        config = get_config()
        prayer_service = PrayerService(config)

        # Get current time in user's timezone
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

        result = prayer_service.get_prayer_times(user_id, date_str, current_time)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Unable to fetch prayer status')}), 500

        # Extract just the status information
        prayers = result.get('prayers', [])
        status_summary = {
            'date': date_str,
            'total_prayers': len(prayers),
            'completed': len([p for p in prayers if p.get('completed', False)]),
            'missed': len([p for p in prayers if p.get('prayer_status') == 'missed']),
            'pending': len([p for p in prayers if p.get('prayer_status') == 'pending']),
            'qada': len([p for p in prayers if p.get('prayer_status') == 'qada'])
        }

        return jsonify(status_summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/streak', methods=['GET'])
@jwt_required()
def get_prayer_streak():
    """Get prayer streak information for the current user."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get streak information from the service layer
        config = get_config()
        prayer_service = PrayerService(config)

        # Get current time in user's timezone
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

        # Calculate streak (simplified implementation)
        # This could be enhanced with a dedicated streak calculation method
        today = current_time.date()
        streak_days = 0

        for i in range(30):  # Check last 30 days
            check_date = today - timedelta(days=i)
            result = prayer_service.get_prayer_times(user_id, check_date.strftime('%Y-%m-%d'), current_time)

            if result.get('success'):
                prayers = result.get('prayers', [])
                completed_count = len([p for p in prayers if p.get('completed', False)])

                if completed_count >= 5:  # All 5 prayers completed
                    streak_days += 1
                else:
                    break
            else:
                break

        return jsonify({
            'current_streak': streak_days,
            'last_updated': today.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/auto-update', methods=['POST'])
@jwt_required()
def auto_update_prayer_status():
    """Manually trigger prayer status update."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use the modern service layer
        config = get_config()
        prayer_service = PrayerService(config)

        # Get current time in user's timezone
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

        # Get today's prayers and update their status
        result = prayer_service.get_prayer_times(user_id, None, current_time)

        if result.get('success'):
            return jsonify({'message': 'Prayer status updated successfully'}), 200
        return jsonify({'error': 'Failed to update prayer status'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
