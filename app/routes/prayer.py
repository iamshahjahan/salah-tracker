from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerType, PrayerStatus
from datetime import datetime, date, timedelta, time
import requests
import pytz

prayer_bp = Blueprint('prayer', __name__)

def get_prayer_time_window(prayer_type, prayer_time, prayer_date, all_prayer_times=None):
    """
    Get the valid time window for completing a prayer using Islamic methodology.
    Each prayer ends when the next prayer begins.
    """
    prayer_time_obj = datetime.strptime(prayer_time, '%H:%M').time()
    prayer_datetime = datetime.combine(prayer_date, prayer_time_obj)
    start_time = prayer_datetime

    # If prayer times are provided, use them; otherwise use fallbacks
    if all_prayer_times:
        prayer_times = all_prayer_times
    else:
        # Fallback prayer times for basic calculation
        prayer_times = {
            PrayerType.FAJR: prayer_time_obj,
            PrayerType.DHUHR: (datetime.combine(prayer_date, prayer_time_obj) + timedelta(hours=6)).time(),
            PrayerType.ASR: (datetime.combine(prayer_date, prayer_time_obj) + timedelta(hours=9)).time(),
            PrayerType.MAGHRIB: (datetime.combine(prayer_date, prayer_time_obj) + timedelta(hours=12)).time(),
            PrayerType.ISHA: (datetime.combine(prayer_date, prayer_time_obj) + timedelta(hours=14)).time()
        }

    # Determine end time based on Islamic methodology
    if prayer_type == PrayerType.FAJR:
        # Fajr ends at Sunrise (use Dhuhr as approximation)
        if PrayerType.DHUHR in prayer_times:
            end_time = datetime.combine(prayer_date, prayer_times[PrayerType.DHUHR])
        else:
            # Fallback: 6 hours after Fajr (approximate sunrise)
            end_time = prayer_datetime + timedelta(hours=6)
            
    elif prayer_type == PrayerType.DHUHR:
        # Dhuhr ends at Asr
        if PrayerType.ASR in prayer_times:
            end_time = datetime.combine(prayer_date, prayer_times[PrayerType.ASR])
        else:
            # Fallback: 3 hours after Dhuhr
            end_time = prayer_datetime + timedelta(hours=3)
            
    elif prayer_type == PrayerType.ASR:
        # Asr ends at Maghrib
        if PrayerType.MAGHRIB in prayer_times:
            end_time = datetime.combine(prayer_date, prayer_times[PrayerType.MAGHRIB])
        else:
            # Fallback: 2 hours after Asr
            end_time = prayer_datetime + timedelta(hours=2)
            
    elif prayer_type == PrayerType.MAGHRIB:
        # Maghrib ends at Isha
        if PrayerType.ISHA in prayer_times:
            end_time = datetime.combine(prayer_date, prayer_times[PrayerType.ISHA])
        else:
            # Fallback: 1.5 hours after Maghrib
            end_time = prayer_datetime + timedelta(hours=1, minutes=30)
            
    elif prayer_type == PrayerType.ISHA:
        # Isha ends at next day's Fajr
        # For simplicity, we'll use 8 hours after Isha (until approximately next day's Fajr)
        end_time = prayer_datetime + timedelta(hours=8)
    else:
        # Default fallback
        end_time = prayer_datetime + timedelta(hours=2)

    return start_time, end_time

def is_prayer_time_valid(prayer_type, prayer_time, prayer_date, completion_time=None, user=None):
    """Check if the current time is within the valid window for completing a prayer"""
    if completion_time is None:
        if user:
            user_tz = pytz.timezone(user.timezone)
            completion_time = datetime.now(user_tz)
        else:
            completion_time = datetime.now()

    start_time, end_time = get_prayer_time_window(prayer_type, prayer_time, prayer_date)
    
    # Make timezone-aware if completion_time is timezone-aware
    if completion_time.tzinfo is not None:
        # Convert naive datetimes to timezone-aware
        if user:
            user_tz = pytz.timezone(user.timezone)
            start_time = user_tz.localize(start_time)
            end_time = user_tz.localize(end_time)

    return start_time <= completion_time <= end_time

def is_prayer_missed(prayer_type, prayer_time, prayer_date, completion_time=None, user=None):
    """Check if a prayer has been missed (past its valid time window)"""
    if completion_time is None:
        if user:
            user_tz = pytz.timezone(user.timezone)
            completion_time = datetime.now(user_tz)
        else:
            completion_time = datetime.now()

    start_time, end_time = get_prayer_time_window(prayer_type, prayer_time, prayer_date)
    
    # Make timezone-aware if completion_time is timezone-aware
    if completion_time.tzinfo is not None:
        # Convert naive datetimes to timezone-aware
        if user:
            user_tz = pytz.timezone(user.timezone)
            start_time = user_tz.localize(start_time)
            end_time = user_tz.localize(end_time)

    return completion_time > end_time

def auto_update_prayer_status(user_id, prayer_date):
    """Automatically update prayer completion status based on current time"""
    try:
        # Get user for timezone
        user = User.query.get(user_id)
        if not user:
            return False
            
        # Get all prayers for the given date
        prayers = Prayer.query.filter(Prayer.prayer_date == prayer_date).all()
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)

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
            if is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time, user):
                # Create a missed prayer record
                missed_completion = PrayerCompletion(
                    user_id=user_id,
                    prayer_id=prayer.id,
                    marked_at=None,  # No completion timestamp for missed prayers
                    status=PrayerStatus.MISSED,  # Mark as missed (can be moved to qada)
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

    # Parse the date to get year, month, day
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        year = target_date.year
        month = target_date.month
        day = target_date.day
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

    # Using Aladhan Calendar API (more reliable than timings API)
    url = f"https://api.aladhan.com/v1/calendar/{year}/{month}"
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
            # Find the specific day in the calendar data
            for day_data in data['data']:
                if day_data['date']['gregorian']['day'] == str(day):
                    timings = day_data['timings']
                    # Remove timezone info from times (e.g., "05:10 (IST)" -> "05:10")
                    return {
                        'Fajr': timings['Fajr'].split(' ')[0],
                        'Dhuhr': timings['Dhuhr'].split(' ')[0],
                        'Asr': timings['Asr'].split(' ')[0],
                        'Maghrib': timings['Maghrib'].split(' ')[0],
                        'Isha': timings['Isha'].split(' ')[0]
                    }
            
            print(f"Date {date_str} not found in calendar data")
            return None
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
                    user_id=user.id,
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

        # Use the enhanced prayer service to get detailed prayer information
        from app.config.settings import get_config
        from app.services.prayer_service import PrayerService
        
        config = get_config()
        prayer_service = PrayerService(config)
        
        prayers_with_status = []
        for prayer in prayers:
            completion = completion_map.get(prayer.id)
            
            # Get enhanced prayer information using the service
            prayer_info = prayer_service._build_prayer_info(prayer, completion, user, prayer.prayer_date)
            prayers_with_status.append(prayer_info)

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

        # Check if already has a completion record
        existing_completion = PrayerCompletion.query.filter_by(
            user_id=user_id,
            prayer_id=data['prayer_id']
        ).first()

        # Get user's timezone for accurate time comparison
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user_tz = pytz.timezone(user.timezone)
        current_time = datetime.now(user_tz)
        prayer_time_str = prayer.prayer_time.strftime('%H:%M')

        if existing_completion:
            # Handle status transitions
            if existing_completion.status == PrayerStatus.PENDING:
                # Transition from pending to complete
                existing_completion.status = PrayerStatus.COMPLETE
                existing_completion.marked_at = datetime.utcnow()
                existing_completion.notes = data.get('notes', existing_completion.notes)
                db.session.commit()
                message = 'Prayer marked as completed'
            elif existing_completion.status == PrayerStatus.MISSED:
                # Transition from missed to qada
                existing_completion.status = PrayerStatus.QADA
                existing_completion.marked_at = datetime.utcnow()
                existing_completion.notes = data.get('notes', existing_completion.notes)
                db.session.commit()
                message = 'Prayer marked as Qada (missed prayer)'
            else:
                # Already in terminal state (COMPLETE or QADA)
                return jsonify({'error': 'Prayer already completed. You can only complete each prayer once.'}), 400
        else:
            # Create new completion record
            if not is_prayer_time_valid(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time, user):
                # Check if it's a missed prayer
                if is_prayer_missed(prayer.prayer_type, prayer_time_str, prayer.prayer_date, current_time, user):
                    # Create as missed (can be moved to qada)
                    status = PrayerStatus.MISSED
                    message = 'Prayer marked as missed (can be completed as Qada)'
                else:
                    # Too early to complete this prayer
                    return jsonify({
                        'error': f'Cannot complete {prayer.prayer_type.value} prayer yet. Please wait until the prayer time.',
                        'prayer_time': prayer_time_str,
                        'current_time': current_time.strftime('%H:%M')
                    }), 400
            else:
                # Valid time for completion - create as pending
                status = PrayerStatus.PENDING
                message = 'Prayer marked as pending (can be completed)'

            completion = PrayerCompletion(
                user_id=user_id,
                prayer_id=data['prayer_id'],
                marked_at=None,  # No timestamp for pending/missed
                status=status,
                notes=data.get('notes')
            )

            db.session.add(completion)
            db.session.commit()

        return jsonify({
            'message': message,
            'completion': (existing_completion if existing_completion else completion).to_dict()
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
def get_prayer_status_for_date(date_str):
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
            prayer_date = completion.prayer.created_at.date()
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
            'last_completion': completions[0].marked_at.isoformat() if completions else None
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
                    user_id=user.id,
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

        # Use the enhanced prayer service to get detailed prayer information
        from app.config.settings import get_config
        from app.services.prayer_service import PrayerService
        
        config = get_config()
        prayer_service = PrayerService(config)
        
        prayer_data = []
        for prayer in prayers:
            completion = PrayerCompletion.query.filter_by(
                user_id=user_id,
                prayer_id=prayer.id
            ).first()

            # Get enhanced prayer information using the service
            prayer_info = prayer_service._build_prayer_info(prayer, completion, user, target_date)
            prayer_data.append(prayer_info)

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
            # Only allow transition from MISSED to QADA
            if existing_completion.status == PrayerStatus.MISSED:
                existing_completion.status = PrayerStatus.QADA
                existing_completion.notes = notes
                existing_completion.marked_at = datetime.utcnow()
            else:
                return jsonify({'error': 'Can only mark missed prayers as Qada'}), 400
        else:
            # Create new Qada completion (should only happen for missed prayers)
            qada_completion = PrayerCompletion(
                user_id=user_id,
                prayer_id=prayer_id,
                marked_at=datetime.utcnow(),
                status=PrayerStatus.QADA,
                notes=notes
            )
            db.session.add(qada_completion)

        db.session.commit()

        return jsonify({
            'message': 'Prayer marked as Qada successfully',
            'completion': (existing_completion if existing_completion else qada_completion).to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
