from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerType
from datetime import datetime, date, timedelta, time
import requests
import pytz

prayer_bp = Blueprint('prayer', __name__)

def get_prayer_time_window(prayer_type, prayer_time, prayer_date):
    """Get the valid time window for completing a prayer"""
    prayer_time_obj = datetime.strptime(prayer_time, '%H:%M').time()

    # Define prayer time windows (in minutes)
    time_windows = {
        PrayerType.FAJR: 30,      # 30 minutes after Fajr time
        PrayerType.DHUHR: 30,     # 30 minutes after Dhuhr time
        PrayerType.ASR: 30,       # 30 minutes after Asr time
        PrayerType.MAGHRIB: 20,   # 20 minutes after Maghrib time
        PrayerType.ISHA: 30       # 30 minutes after Isha time
    }

    window_minutes = time_windows.get(prayer_type, 30)

    # Calculate start and end times
    prayer_datetime = datetime.combine(prayer_date, prayer_time_obj)
    start_time = prayer_datetime
    end_time = prayer_datetime + timedelta(minutes=window_minutes)

    # Special case for Fajr - it can be completed until sunrise (next prayer time)
    if prayer_type == PrayerType.FAJR:
        # For Fajr, extend until Dhuhr time (simplified)
        end_time = prayer_datetime + timedelta(hours=6)  # Approximate sunrise time

    return start_time, end_time

def is_prayer_time_valid(prayer_type, prayer_time, prayer_date, completion_time=None):
    """Check if the current time is within the valid window for completing a prayer"""
    if completion_time is None:
        completion_time = datetime.now()

    start_time, end_time = get_prayer_time_window(prayer_type, prayer_time, prayer_date)

    return start_time <= completion_time <= end_time

def is_prayer_missed(prayer_type, prayer_time, prayer_date, completion_time=None):
    """Check if a prayer has been missed (past its valid time window)"""
    if completion_time is None:
        completion_time = datetime.now()

    start_time, end_time = get_prayer_time_window(prayer_type, prayer_time, prayer_date)

    return completion_time > end_time

def auto_update_prayer_status(user_id, prayer_date):
    """Automatically update prayer completion status based on current time"""
    try:
        # Get all prayers for the given date
        prayers = Prayer.query.filter(Prayer.prayer_date == prayer_date).all()
        current_time = datetime.now()

        for prayer in prayers:
            prayer_time_str = prayer.prayer_time.strftime('%H:%M')

            # Check if prayer is already completed
            existing_completion = PrayerCompletion.query.filter_by(
                user_id=user_id,
                prayer_id=prayer.id
            ).first()

            if existing_completion:
                continue  # Skip if already completed

            # Check if prayer time has passed and should be marked as missed
            if is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time):
                # Create a missed prayer record
                missed_completion = PrayerCompletion(
                    user_id=user_id,
                    prayer_id=prayer.id,
                    completed_at=current_time,
                    is_late=True,
                    is_qada=False,  # This is a missed prayer, not Qada
                    notes="Automatically marked as missed"
                )
                db.session.add(missed_completion)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error in auto_update_prayer_status: {e}")
        return False

def get_prayer_times(lat, lng, date_str=None):
    """Get prayer times from external API"""
    if not date_str:
        date_str = date.today().isoformat()

    # Using Aladhan API (free, no API key required)
    url = f"http://api.aladhan.com/v1/timings/{date_str}"
    params = {
        'latitude': lat,
        'longitude': lng,
        'method': 2,  # Islamic Society of North America (ISNA)
        'school': 1   # Shafi
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            timings = data['data']['timings']
            return {
                'Fajr': timings['Fajr'],
                'Dhuhr': timings['Dhuhr'],
                'Asr': timings['Asr'],
                'Maghrib': timings['Maghrib'],
                'Isha': timings['Isha']
            }
    except Exception as e:
        print(f"Error fetching prayer times: {e}")

    return None

@prayer_bp.route('/times', methods=['GET'])
@jwt_required()
def get_prayer_times_for_user():
    """Get prayer times for the current user's location"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.location_lat or not user.location_lng:
            return jsonify({'error': 'User location not set'}), 400

        date_str = request.args.get('date', date.today().isoformat())
        prayer_times = get_prayer_times(user.location_lat, user.location_lng, date_str)

        if not prayer_times:
            return jsonify({'error': 'Unable to fetch prayer times'}), 500

        # First, check if prayers already exist for this date and location
        prayer_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # Use a small tolerance for float comparison
        lat_tolerance = 0.0001
        lng_tolerance = 0.0001
        existing_prayers = Prayer.query.filter(
            Prayer.prayer_date == prayer_date,
            Prayer.location_lat.between(user.location_lat - lat_tolerance, user.location_lat + lat_tolerance),
            Prayer.location_lng.between(user.location_lng - lng_tolerance, user.location_lng + lng_tolerance)
        ).all()

        # If prayers already exist, use them
        if existing_prayers and len(existing_prayers) >= 5:  # All 5 prayers exist
            prayers = existing_prayers
        else:
            # Convert to Prayer objects and save to database
            prayers = []
            for prayer_type, time_str in prayer_times.items():
                prayer_time = datetime.strptime(time_str, '%H:%M').time()

                prayer = Prayer(
                    prayer_type=PrayerType(prayer_type),
                    prayer_date=prayer_date,
                    prayer_time=prayer_time,
                    location_lat=user.location_lat,
                    location_lng=user.location_lng,
                    timezone=user.timezone
                )
                db.session.add(prayer)
                prayers.append(prayer)

            # Commit only if we created new prayers
            db.session.commit()

        # Auto-update prayer status based on current time
        auto_update_prayer_status(user_id, prayer_date)

        # Get user's completions for these prayers
        prayer_ids = [prayer.id for prayer in prayers]
        completions = PrayerCompletion.query.filter(
            PrayerCompletion.user_id == user_id,
            PrayerCompletion.prayer_id.in_(prayer_ids)
        ).all()

        # Create completion map
        completion_map = {comp.prayer_id: comp for comp in completions}

        # Add completion status to prayers
        prayers_with_status = []
        for prayer in prayers:
            prayer_dict = prayer.to_dict()
            completion = completion_map.get(prayer.id)

            # Check time validation for this prayer
            prayer_time_str = prayer.prayer_time.strftime('%H:%M')
            current_time = datetime.now()

            can_complete = is_prayer_time_valid(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time)
            is_missed = is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time)

            prayer_dict['completed'] = completion is not None
            prayer_dict['can_complete'] = can_complete
            prayer_dict['is_missed'] = is_missed
            prayer_dict['completion'] = completion.to_dict() if completion else None
            # Allow Qada marking for missed prayers or late prayers that aren't already Qada
            can_mark_qada = user.created_at and prayer.prayer_date >= user.created_at.date()
            if completion:
                # If prayer is completed, only allow Qada if it's late but not already Qada
                can_mark_qada = can_mark_qada and completion.is_late and not completion.is_qada
            else:
                # If prayer is not completed, allow Qada if it's missed
                can_mark_qada = can_mark_qada and is_missed

            prayer_dict['can_mark_qada'] = can_mark_qada
            prayers_with_status.append(prayer_dict)

        return jsonify({
            'date': date_str,
            'prayers': prayers_with_status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_prayer():
    """Mark a prayer as completed"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('prayer_id'):
            return jsonify({'error': 'prayer_id is required'}), 400

        prayer = Prayer.query.get(data['prayer_id'])
        if not prayer:
            return jsonify({'error': 'Prayer not found'}), 404

        # Check if already completed
        existing_completion = PrayerCompletion.query.filter_by(
            user_id=user_id,
            prayer_id=data['prayer_id']
        ).first()

        if existing_completion:
            return jsonify({'error': 'Prayer already completed. You can only complete each prayer once.'}), 400

        current_time = datetime.now()
        prayer_time_str = prayer.prayer_time.strftime('%H:%M')

        # Check if prayer time is valid for completion
        if not is_prayer_time_valid(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time):
            # Check if it's a missed prayer (Qada)
            if is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time):
                # Allow completion as Qada
                is_qada = True
                is_late = True
            else:
                # Too early to complete this prayer
                return jsonify({
                    'error': f'Cannot complete {prayer.prayer_type.value} prayer yet. Please wait until the prayer time.',
                    'prayer_time': prayer_time_str,
                    'current_time': current_time.strftime('%H:%M')
                }), 400
        else:
            # Valid time for completion
            is_qada = False
            is_late = False

        completion = PrayerCompletion(
            user_id=user_id,
            prayer_id=data['prayer_id'],
            is_late=is_late,
            is_qada=is_qada,
            notes=data.get('notes')
        )

        db.session.add(completion)
        db.session.commit()

        message = 'Prayer marked as completed'
        if is_qada:
            message = 'Prayer marked as Qada (missed prayer)'
        elif is_late:
            message = 'Prayer marked as completed (late)'

        return jsonify({
            'message': message,
            'completion': completion.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/completions', methods=['GET'])
@jwt_required()
def get_prayer_completions():
    """Get user's prayer completions for a date range"""
    try:
        user_id = get_jwt_identity()
        start_date = request.args.get('start_date', date.today().isoformat())
        end_date = request.args.get('end_date', date.today().isoformat())

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

        completions = db.session.query(PrayerCompletion).join(Prayer).filter(
            PrayerCompletion.user_id == user_id,
            Prayer.prayer_date >= start_date_obj,
            Prayer.prayer_date <= end_date_obj
        ).order_by(Prayer.prayer_date, Prayer.prayer_time).all()

        return jsonify({
            'completions': [completion.to_dict() for completion in completions]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/status/<date_str>', methods=['GET'])
@jwt_required()
def get_prayer_status_for_date():
    """Get prayer completion status for a specific date"""
    try:
        user_id = get_jwt_identity()
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get all prayers for the date
        prayers = Prayer.query.filter_by(prayer_date=date_obj).all()

        # Get completions for the user and date
        completions = PrayerCompletion.query.join(Prayer).filter(
            PrayerCompletion.user_id == user_id,
            Prayer.prayer_date == date_obj
        ).all()

        # Create status map
        completion_map = {comp.prayer_id: comp for comp in completions}

        status = []
        for prayer in prayers:
            completion = completion_map.get(prayer.id)
            status.append({
                'prayer': prayer.to_dict(),
                'completed': completion is not None,
                'completion': completion.to_dict() if completion else None
            })

        return jsonify({
            'date': date_str,
            'status': status
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/streak', methods=['GET'])
@jwt_required()
def get_prayer_streak():
    """Get user's current prayer streak"""
    try:
        user_id = get_jwt_identity()

        # Get all completions ordered by date
        completions = db.session.query(PrayerCompletion).join(Prayer).filter(
            PrayerCompletion.user_id == user_id
        ).order_by(Prayer.prayer_date.desc()).all()

        if not completions:
            return jsonify({'streak': 0, 'message': 'No prayers completed yet'}), 200

        # Calculate streak
        streak = 0
        current_date = date.today()

        # Group completions by date
        completions_by_date = {}
        for completion in completions:
            prayer_date = completion.prayer.completed_at.date()
            if prayer_date not in completions_by_date:
                completions_by_date[prayer_date] = []
            completions_by_date[prayer_date].append(completion)

        # Count consecutive days with all 5 prayers completed
        for i in range(365):  # Check up to 1 year back
            check_date = current_date - timedelta(days=i)

            if check_date in completions_by_date:
                # Check if all 5 prayers were completed on this date
                daily_completions = completions_by_date[check_date]
                if len(daily_completions) >= 5:  # All 5 prayers completed
                    streak += 1
                else:
                    break
            else:
                break

        return jsonify({
            'streak': streak,
            'last_completion': completions[0].completed_at.isoformat() if completions else None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/times/<date_str>', methods=['GET'])
@jwt_required()
def get_prayer_times_for_date(date_str):
    """Get prayer times for a specific date"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.location_lat or not user.location_lng:
            return jsonify({'error': 'User location not set'}), 400

        # Validate date format
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Check if prayers already exist for this date and location
        lat_tolerance = 0.0001
        lng_tolerance = 0.0001
        existing_prayers = Prayer.query.filter(
            Prayer.prayer_date == target_date,
            Prayer.location_lat.between(user.location_lat - lat_tolerance, user.location_lat + lng_tolerance),
            Prayer.location_lng.between(user.location_lng - lng_tolerance, user.location_lng + lng_tolerance)
        ).all()

        # If prayers already exist, use them
        if existing_prayers and len(existing_prayers) >= 5:
            prayers = existing_prayers
        else:
            # Get prayer times from API
            prayer_times = get_prayer_times(user.location_lat, user.location_lng, date_str)

            if not prayer_times:
                return jsonify({'error': 'Failed to fetch prayer times'}), 500

            # Convert to Prayer objects and save to database
            prayers = []
            for prayer_type, time_str in prayer_times.items():
                prayer_time = datetime.strptime(time_str, '%H:%M').time()

                prayer = Prayer(
                    prayer_type=PrayerType(prayer_type),
                    prayer_date=target_date,
                    prayer_time=prayer_time,
                    location_lat=user.location_lat,
                    location_lng=user.location_lng,
                    timezone=user.timezone
                )
                db.session.add(prayer)
                prayers.append(prayer)

            # Commit only if we created new prayers
            db.session.commit()

        # Auto-update prayer status based on current time
        auto_update_prayer_status(user_id, target_date)

        # Get completion status for each prayer
        prayer_data = []
        for prayer in prayers:
            completion = PrayerCompletion.query.filter_by(
                user_id=user_id,
                prayer_id=prayer.id
            ).first()

            # Check time validation for this prayer
            prayer_time_str = prayer.prayer_time.strftime('%H:%M')
            current_time = datetime.now()

            can_complete = is_prayer_time_valid(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time)
            is_missed = is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time)

            prayer_data.append({
                'id': prayer.id,
                'prayer_type': prayer.prayer_type.value,
                'prayer_time': prayer.prayer_time.strftime('%H:%M'),
                'completed': completion is not None,
                'can_complete': can_complete,
                'is_missed': is_missed,
                'completion': {
                    'completed_at': completion.completed_at.isoformat() if completion else None,
                    'is_late': completion.is_late if completion else False,
                    'is_qada': completion.is_qada if completion else False
                } if completion else None,
                # Allow Qada marking for missed prayers or late prayers that aren't already Qada
                'can_mark_qada': (
                    user.created_at and prayer.prayer_date >= user.created_at.date() and (
                        (completion and completion.is_late and not completion.is_qada) or
                        (not completion and is_missed)
                    )
                )
            })

        return jsonify({
            'date': date_str,
            'prayers': prayer_data
        })

    except Exception as e:
        print(f"Error in get_prayer_times_for_date: {e}")
        return jsonify({'error': 'Failed to get prayer times for date'}), 500

@prayer_bp.route('/auto-update', methods=['POST'])
@jwt_required()
def auto_update_prayers():
    """Manually trigger automatic prayer status update"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('date'):
            return jsonify({'error': 'date is required'}), 400

        target_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Auto-update prayer status
        success = auto_update_prayer_status(user_id, target_date)

        if success:
            return jsonify({'message': 'Prayer status updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update prayer status'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/mark-qada', methods=['POST'])
@jwt_required()
def mark_prayer_qada():
    """Mark a missed prayer as Qada (makeup prayer)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('prayer_id'):
            return jsonify({'error': 'prayer_id is required'}), 400

        prayer_id = data['prayer_id']
        notes = data.get('notes', 'Marked as Qada')

        # Get the prayer
        prayer = Prayer.query.get(prayer_id)
        if not prayer:
            return jsonify({'error': 'Prayer not found'}), 404

        # Get user to check account creation date
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if prayer date is after account creation
        if user.created_at and prayer.prayer_date < user.created_at.date():
            return jsonify({'error': 'Cannot mark prayers as Qada before account creation date'}), 400

        # Check if prayer is already completed
        existing_completion = PrayerCompletion.query.filter_by(
            user_id=user_id,
            prayer_id=prayer_id
        ).first()

        if existing_completion:
            # Update existing completion to mark as Qada
            existing_completion.is_qada = True
            existing_completion.is_late = True
            existing_completion.notes = notes
            existing_completion.completed_at = datetime.utcnow()
        else:
            # Create new Qada completion
            qada_completion = PrayerCompletion(
                user_id=user_id,
                prayer_id=prayer_id,
                completed_at=datetime.utcnow(),
                is_late=True,
                is_qada=True,
                notes=notes
            )
            db.session.add(qada_completion)

        db.session.commit()

        return jsonify({
            'message': 'Prayer marked as Qada successfully',
            'completion': qada_completion.to_dict() if not existing_completion else existing_completion.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
