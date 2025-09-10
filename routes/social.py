from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from flask_mail import Message
from mail_config import mail
from models.user import User
from models.family import FamilyMember
from models.prayer import Prayer, PrayerCompletion
from datetime import datetime, date, timedelta
import requests

social_bp = Blueprint('social', __name__)

@social_bp.route('/family', methods=['GET'])
@jwt_required()
def get_family_members():
    """Get user's family members"""
    try:
        user_id = get_jwt_identity()
        family_members = FamilyMember.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'family_members': [member.to_dict() for member in family_members]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/family', methods=['POST'])
@jwt_required()
def add_family_member():
    """Add a new family member"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('name') or not data.get('relationship'):
            return jsonify({'error': 'Name and relationship are required'}), 400
        
        family_member = FamilyMember(
            user_id=user_id,
            name=data['name'],
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            relationship=data['relationship'],
            reminder_enabled=data.get('reminder_enabled', True)
        )
        
        db.session.add(family_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Family member added successfully',
            'family_member': family_member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@social_bp.route('/family/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_family_member(member_id):
    """Update a family member"""
    try:
        user_id = get_jwt_identity()
        family_member = FamilyMember.query.filter_by(
            id=member_id, 
            user_id=user_id
        ).first()
        
        if not family_member:
            return jsonify({'error': 'Family member not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            family_member.name = data['name']
        if 'phone_number' in data:
            family_member.phone_number = data['phone_number']
        if 'email' in data:
            family_member.email = data['email']
        if 'relationship' in data:
            family_member.relationship = data['relationship']
        if 'reminder_enabled' in data:
            family_member.reminder_enabled = data['reminder_enabled']
        
        family_member.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Family member updated successfully',
            'family_member': family_member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@social_bp.route('/family/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_family_member(member_id):
    """Delete a family member"""
    try:
        user_id = get_jwt_identity()
        family_member = FamilyMember.query.filter_by(
            id=member_id, 
            user_id=user_id
        ).first()
        
        if not family_member:
            return jsonify({'error': 'Family member not found'}), 404
        
        db.session.delete(family_member)
        db.session.commit()
        
        return jsonify({'message': 'Family member deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@social_bp.route('/remind', methods=['POST'])
@jwt_required()
def send_prayer_reminder():
    """Send prayer reminder to family members"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('prayer_type') or not data.get('member_ids'):
            return jsonify({'error': 'Prayer type and member IDs are required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get family members
        family_members = FamilyMember.query.filter(
            FamilyMember.id.in_(data['member_ids']),
            FamilyMember.user_id == user_id,
            FamilyMember.reminder_enabled == True
        ).all()
        
        if not family_members:
            return jsonify({'error': 'No family members found or enabled for reminders'}), 400
        
        # Send reminders
        sent_count = 0
        for member in family_members:
            try:
                if member.email:
                    send_email_reminder(user, member, data['prayer_type'])
                    sent_count += 1
                elif member.phone_number:
                    send_sms_reminder(user, member, data['prayer_type'])
                    sent_count += 1
            except Exception as e:
                print(f"Error sending reminder to {member.name}: {e}")
                continue
        
        return jsonify({
            'message': f'Prayer reminders sent to {sent_count} family members',
            'sent_count': sent_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@social_bp.route('/motivation', methods=['GET'])
@jwt_required()
def get_motivational_content():
    """Get motivational content for the user"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's recent completion rate
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        total_prayers = db.session.query(Prayer).filter(
            Prayer.prayer_date >= start_date,
            Prayer.prayer_date <= end_date
        ).count()
        
        completed_prayers = db.session.query(PrayerCompletion).join(Prayer).filter(
            PrayerCompletion.user_id == user_id,
            Prayer.prayer_date >= start_date,
            Prayer.prayer_date <= end_date
        ).count()
        
        completion_rate = (completed_prayers / total_prayers * 100) if total_prayers > 0 else 0
        
        # Get motivational messages based on performance
        if completion_rate >= 90:
            message = "MashaAllah! You're doing excellent with your prayers. Keep up the great work!"
            emoji = "🌟"
        elif completion_rate >= 70:
            message = "Good job! You're maintaining a strong prayer routine. Try to increase it even more!"
            emoji = "👍"
        elif completion_rate >= 50:
            message = "You're making progress! Remember, every prayer counts. Keep striving for consistency."
            emoji = "💪"
        else:
            message = "Don't give up! Every journey begins with a single step. Start with one prayer at a time."
            emoji = "🤲"
        
        return jsonify({
            'completion_rate': round(completion_rate, 2),
            'message': message,
            'emoji': emoji,
            'period': '7 days'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_email_reminder(user, family_member, prayer_type):
    """Send email reminder to family member"""
    try:
        msg = Message(
            subject=f"Prayer Reminder - {prayer_type}",
            sender=user.email,
            recipients=[family_member.email]
        )
        msg.body = f"""
Assalamu Alaikum {family_member.name},

{user.first_name} {user.last_name} is reminding you that it's time for {prayer_type} prayer.

May Allah accept your prayers and grant you peace.

Best regards,
SalahReminders Team
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def send_sms_reminder(user, family_member, prayer_type):
    """Send SMS reminder to family member (placeholder - would need SMS service integration)"""
    try:
        # This would integrate with a service like Twilio
        # For now, we'll just log the action
        print(f"SMS reminder sent to {family_member.phone_number}: {prayer_type} prayer reminder from {user.first_name}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
        raise
