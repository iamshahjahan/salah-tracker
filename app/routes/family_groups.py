"""Family Groups API routes.

This module defines API endpoints for managing family prayer groups,
including creating groups, joining groups, and managing members.
"""


from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.family_group_service import FamilyGroupService

# Create blueprint
family_groups_bp = Blueprint('family_groups', __name__)


@family_groups_bp.route('/create', methods=['POST'])
@jwt_required()
def create_family_group():
    """Create a new family group."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Group name is required'}), 400

        family_group_service = FamilyGroupService()
        result = family_group_service.create_family_group(
            user_id=user_id,
            name=data['name'],
            description=data.get('description', '')
        )

        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/join', methods=['POST'])
@jwt_required()
def join_family_group():
    """Join a family group using invite code."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('invite_code'):
            return jsonify({'error': 'Invite code is required'}), 400

        family_group_service = FamilyGroupService()
        result = family_group_service.join_family_group(
            user_id=user_id,
            invite_code=data['invite_code']
        )

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/my-groups', methods=['GET'])
@jwt_required()
def get_my_family_groups():
    """Get family groups for the current user."""
    try:
        user_id = get_jwt_identity()

        family_group_service = FamilyGroupService()
        result = family_group_service.get_user_family_groups(user_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_family_group(group_id):
    """Get details of a specific family group."""
    try:
        user_id = get_jwt_identity()

        family_group_service = FamilyGroupService()
        result = family_group_service.get_family_group_details(group_id, user_id)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/<int:group_id>/members', methods=['GET'])
@jwt_required()
def get_family_group_members(group_id):
    """Get members of a family group."""
    try:
        user_id = get_jwt_identity()

        family_group_service = FamilyGroupService()
        result = family_group_service.get_family_group_members(group_id, user_id)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 403

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@jwt_required()
def leave_family_group(group_id):
    """Leave a family group."""
    try:
        user_id = get_jwt_identity()

        family_group_service = FamilyGroupService()
        result = family_group_service.leave_family_group(group_id, user_id)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@family_groups_bp.route('/<int:group_id>/regenerate-invite', methods=['POST'])
@jwt_required()
def regenerate_invite_code(group_id):
    """Regenerate invite code for a family group (admin only)."""
    try:
        user_id = get_jwt_identity()

        family_group_service = FamilyGroupService()
        result = family_group_service.regenerate_invite_code(group_id, user_id)

        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 403

    except Exception as e:
        return jsonify({'error': str(e)}), 500
