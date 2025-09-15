from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config.database import db
from app.models.user import User
from app.services.auth_service import AuthService
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Set default location to Bangalore, India if not provided
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')
        timezone = data.get('timezone')

        if not location_lat or not location_lng:
            # Default to Bangalore, India
            location_lat = 12.9716
            location_lng = 77.5946
            timezone = 'Asia/Kolkata'

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number'),
            location_lat=location_lat,
            location_lng=location_lng,
            timezone=timezone,
            notification_enabled=data.get('notification_enabled', True)
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=user.id)

        # Send email verification automatically
        try:
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            verification_result = auth_service.send_email_verification(user.id)
            
            if verification_result['success']:
                return jsonify({
                    'message': 'User registered successfully. Please check your email for verification code.',
                    'access_token': access_token,
                    'user': user.to_dict(),
                    'verification_sent': True
                }), 201
            else:
                # Registration successful but email verification failed
                return jsonify({
                    'message': 'User registered successfully. Email verification could not be sent.',
                    'access_token': access_token,
                    'user': user.to_dict(),
                    'verification_sent': False,
                    'verification_error': verification_result.get('error', 'Unknown error')
                }), 201
        except Exception as email_error:
            # Registration successful but email verification failed
            return jsonify({
                'message': 'User registered successfully. Email verification could not be sent.',
                'access_token': access_token,
                'user': user.to_dict(),
                'verification_sent': False,
                'verification_error': str(email_error)
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token"""
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create access token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'location_lat' in data:
            user.location_lat = data['location_lat']
        if 'location_lng' in data:
            user.location_lng = data['location_lng']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'city' in data:
            user.city = data['city']
        if 'country' in data:
            user.country = data['country']
        if 'fiqh_method' in data:
            user.fiqh_method = data['fiqh_method']
        if 'language' in data:
            # Validate language option
            if data['language'] in ['ar', 'en']:
                user.language = data['language']
            else:
                return jsonify({'error': 'Language must be either "ar" or "en"'}), 400
        if 'notification_enabled' in data:
            user.notification_enabled = data['notification_enabled']
        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']
        if 'reminder_times' in data:
            user.reminder_times = data['reminder_times']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user's password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400

        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Set new password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/send-verification', methods=['POST'])
@jwt_required()
def send_email_verification():
    """Send email verification code to current user"""
    try:
        user_id = get_jwt_identity()
        auth_service = AuthService()

        result = auth_service.send_email_verification(user_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user's email with verification code"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('code'):
            return jsonify({'error': 'Email and verification code are required'}), 400

        auth_service = AuthService()
        result = auth_service.verify_email(data['email'], data['code'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/send-login-otp', methods=['POST'])
def send_login_otp():
    """Send OTP for login to user's email"""
    try:
        data = request.get_json()

        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        auth_service = AuthService()
        result = auth_service.send_login_otp(data['email'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login-with-otp', methods=['POST'])
def login_with_otp():
    """Login user with OTP"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('otp'):
            return jsonify({'error': 'Email and OTP are required'}), 400

        auth_service = AuthService()
        result = auth_service.authenticate_with_otp(data['email'], data['otp'])

        if result['success']:
            return jsonify({
                'message': 'Login successful',
                'access_token': result['access_token'],
                'user': result['user']
            }), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset link to user's email"""
    try:
        data = request.get_json()

        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        auth_service = AuthService()
        result = auth_service.send_password_reset(data['email'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset user's password using verification code"""
    try:
        data = request.get_json()

        if not data.get('code') or not data.get('new_password'):
            return jsonify({'error': 'Reset code and new password are required'}), 400

        auth_service = AuthService()
        result = auth_service.reset_password_with_code(data['code'], data['new_password'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
