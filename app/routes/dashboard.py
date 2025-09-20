from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.config.settings import get_config
from app.models.prayer import Prayer, PrayerCompletion
from app.models.user import User
from app.services import UserService
from app.services.cache_service import cache_service
from config.database import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user's prayer statistics."""
    try:
        user_id = get_jwt_identity()
        # Check cache first
        cached_data = cache_service.get_dashboard_stats(user_id)
        if cached_data:
            return jsonify(cached_data), 200

        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_service = UserService(get_config())

        # Get user statistics
        result = user_service.get_user_statistics(user_id)

        # Check if the service call was successful
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Failed to retrieve statistics')}), 500

        # Cache the result for 10 minutes
        cache_service.set_dashboard_stats(user_id, result, 600)

        return jsonify(result), 200

        # Use account creation date as start date, or last 30 days if requested
        # end_date = date.today()
        # if request.args.get('days'):
        #     days = int(request.args.get('days'))
        #     start_date = end_date - timedelta(days=days)
        # else:
        #     # Use account creation date as start date
        #     start_date = user.created_at.date() if user.created_at else end_date - timedelta(days=30)
        #
        # # Calculate actual days since account creation
        # actual_days = (end_date - start_date).days + 1
        #
        # # Get total prayers in period
        # total_prayers = db.session.query(Prayer).filter(
        #     Prayer.prayer_date >= start_date,
        #     Prayer.prayer_date <= end_date
        # ).count()
        #
        # # Get completed prayers
        # completed_prayers = db.session.query(PrayerCompletion).join(Prayer).filter(
        #     PrayerCompletion.user_id == user_id,
        #     Prayer.prayer_date >= start_date,
        #     Prayer.prayer_date <= end_date
        # ).count()
        #
        # # Get completion rate
        # completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
        #
        # # Get prayers by type
        # prayer_stats = db.session.query(
        #     Prayer.prayer_type,
        #     func.count(PrayerCompletion.id).label('completed'),
        #     func.count(Prayer.id).label('total')
        # ).outerjoin(
        #     PrayerCompletion,
        #     and_(
        #         PrayerCompletion.prayer_id == Prayer.id,
        #         PrayerCompletion.user_id == user_id
        #     )
        # ).filter(
        #     Prayer.prayer_date >= start_date,
        #     Prayer.prayer_date <= end_date
        # ).group_by(Prayer.prayer_type).all()

        # for prayer_type, completed, total in prayer_stats:
        #     prayer_breakdown.append({
        #         'prayer_type': prayer_type.value,
        #         'completed': completed,
        #         'total': total,
        #         'rate': (completed / total * 100) if total > 0 else 0
        #     })

        # Get current streak
        # streak = get_prayer_streak(user_id)

        result = {
            # 'period': {
            #     'start_date': start_date.isoformat(),
            #     'end_date': end_date.isoformat(),
            #     'days': actual_days
            # },
            # 'overall': {
            #     'total_prayers': total_prayers,
            #     'completed_prayers': completed_prayers,
            #     'completion_rate': round(completion_rate, 2)
            # },
            # 'prayer_breakdown': prayer_breakdown,
            # 'current_streak': streak
        }

        # Cache the result for 10 minutes
        cache_service.set_dashboard_stats(user_id, result, 600)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/calendar/<year>/<month>', methods=['GET'])
@jwt_required()
def get_calendar_data(year, month):
    """Get prayer completion data for calendar view."""
    try:
        user_id = get_jwt_identity()

        # Get start and end dates for the month
        start_date = date(int(year), int(month), 1)
        if int(month) == 12:
            end_date = date(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(int(year), int(month) + 1, 1) - timedelta(days=1)

        # Get all prayers for the month
        prayers = Prayer.query.filter(
            Prayer.prayer_date >= start_date,
            Prayer.prayer_date <= end_date
        ).order_by(Prayer.prayer_date, Prayer.prayer_time).all()

        # Get completions for the user
        completions = db.session.query(PrayerCompletion).join(Prayer).filter(
            PrayerCompletion.user_id == user_id,
            Prayer.prayer_date >= start_date,
            Prayer.prayer_date <= end_date
        ).all()

        # Group by date
        calendar_data = {}
        for prayer in prayers:
            prayer_date = prayer.prayer_date.isoformat()
            if prayer_date not in calendar_data:
                calendar_data[prayer_date] = {
                    'date': prayer_date,
                    'prayers': [],
                    'completed_count': 0,
                    'total_count': 0
                }

            # Check if this prayer was completed
            completion = next((c for c in completions if c.prayer_id == prayer.id), None)

            prayer_data = prayer.to_dict()
            prayer_data['completed'] = completion is not None
            prayer_data['completion'] = completion.to_dict() if completion else None

            calendar_data[prayer_date]['prayers'].append(prayer_data)
            calendar_data[prayer_date]['total_count'] += 1
            if completion:
                calendar_data[prayer_date]['completed_count'] += 1

        # Convert to list and sort by date
        calendar_list = sorted(calendar_data.values(), key=lambda x: x['date'])

        return jsonify({
            'year': int(year),
            'month': int(month),
            'calendar_data': calendar_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get recent prayer completion activity."""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 10))

        # Get recent completions
        recent_completions = db.session.query(PrayerCompletion).join(Prayer).filter(
            PrayerCompletion.user_id == user_id
        ).order_by(PrayerCompletion.marked_at.desc()).limit(limit).all()

        return jsonify({
            'recent_completions': [completion.to_dict() for completion in recent_completions]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# def get_prayer_streak(user_id):
#     """Helper function to calculate prayer streak."""
#     try:
#         # Get all completions ordered by date
#         completions = db.session.query(PrayerCompletion).join(Prayer).filter(
#             PrayerCompletion.user_id == user_id
#         ).order_by(Prayer.prayer_date.desc()).all()
#
#         if not completions:
#             return 0
#
#         # Calculate streak
#         streak = 0
#         current_date = date.today()
#
#         # Group completions by date
#         completions_by_date = {}
#         for completion in completions:
#             prayer_date = completion.prayer.prayer_date
#             if prayer_date not in completions_by_date:
#                 completions_by_date[prayer_date] = []
#             completions_by_date[prayer_date].append(completion)
#
#         # Count consecutive days with all 5 prayers completed
#         for i in range(365):  # Check up to 1 year back
#             check_date = current_date - timedelta(days=i)
#
#             if check_date in completions_by_date:
#                 # Check if all 5 prayers were completed on this date
#                 daily_completions = completions_by_date[check_date]
#                 if len(daily_completions) >= 5:  # All 5 prayers completed
#                     streak += 1
#                 else:
#                     break
#             else:
#                 break
#
#         return streak
#
#     except Exception:
#         return 0
