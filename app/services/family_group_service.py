"""Family Group service for managing family prayer groups.

This service handles creating, joining, and managing family prayer groups
with proper validation and authorization.
"""

from typing import Any, Dict

from app.models.family_group import FamilyGroup, FamilyGroupMember
from app.models.user import User

from .base_service import BaseService


class FamilyGroupService(BaseService):
    """Service for managing family prayer groups.

    This service provides methods for creating groups, joining groups,
    managing members, and handling group permissions.
    """

    def create_family_group(self, user_id: int, name: str, description: str = '') -> Dict[str, Any]:
        """Create a new family group.

        Args:
            user_id: ID of the user creating the group.
            name: Name of the family group.
            description: Optional description of the group.

        Returns:
            Dict[str, Any]: Result with success status and group data or error.
        """
        try:
            # Check if user exists
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Generate invite code first
            import random
            import string
            while True:
                invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not FamilyGroup.query.filter_by(invite_code=invite_code).first():
                    break

            # Create the family group
            family_group = self.create_record(
                FamilyGroup,
                name=name,
                description=description,
                admin_user_id=user_id,
                invite_code=invite_code
            )

            self.db_session.commit()

            # Add the creator as a member
            self.create_record(
                FamilyGroupMember,
                family_group_id=family_group.id,
                user_id=user_id,
                role='admin'
            )

            self.logger.info(f"Family group '{name}' created by user {user.email}")

            return {
                'success': True,
                'message': 'Family group created successfully',
                'group': family_group.to_dict(),
                'invite_code': invite_code
            }

        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'create_family_group')

    def join_family_group(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Join a family group using invite code.

        Args:
            user_id: ID of the user joining the group.
            invite_code: Invite code for the group.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Check if user exists
            user = self.get_record_by_id(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }

            # Find the family group by invite code
            family_group = FamilyGroup.query.filter_by(
                invite_code=invite_code,
                is_active=True
            ).first()

            if not family_group:
                return {
                    'success': False,
                    'error': 'Invalid invite code'
                }

            # Check if user is already a member
            existing_member = FamilyGroupMember.query.filter_by(
                family_group_id=family_group.id,
                user_id=user_id,
                is_active=True
            ).first()

            if existing_member:
                return {
                    'success': False,
                    'error': 'You are already a member of this group'
                }

            # Add user to the group
            self.create_record(
                FamilyGroupMember,
                family_group_id=family_group.id,
                user_id=user_id,
                role='member'
            )

            self.logger.info(f"User {user.email} joined family group '{family_group.name}'")

            return {
                'success': True,
                'message': 'Successfully joined the family group',
                'group': family_group.to_dict()
            }

        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'join_family_group')

    def get_user_family_groups(self, user_id: int) -> Dict[str, Any]:
        """Get all family groups for a user.

        Args:
            user_id: ID of the user.

        Returns:
            Dict[str, Any]: Result with user's family groups.
        """
        try:
            # Get user's family group memberships
            memberships = FamilyGroupMember.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()

            groups = []
            for membership in memberships:
                group_data = membership.family_group.to_dict()
                group_data['user_role'] = membership.role
                groups.append(group_data)

            return {
                'success': True,
                'groups': groups,
                'count': len(groups)
            }

        except Exception as e:
            return self.handle_service_error(e, 'get_user_family_groups')

    def get_family_group_details(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """Get details of a specific family group.

        Args:
            group_id: ID of the family group.
            user_id: ID of the user requesting details.

        Returns:
            Dict[str, Any]: Result with group details or error.
        """
        try:
            # Check if user is a member of the group
            membership = FamilyGroupMember.query.filter_by(
                family_group_id=group_id,
                user_id=user_id,
                is_active=True
            ).first()

            if not membership:
                return {
                    'success': False,
                    'error': 'You are not a member of this group'
                }

            group = membership.family_group
            group_data = group.to_dict()
            group_data['user_role'] = membership.role

            return {
                'success': True,
                'group': group_data
            }

        except Exception as e:
            return self.handle_service_error(e, 'get_family_group_details')

    def get_family_group_members(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """Get members of a family group.

        Args:
            group_id: ID of the family group.
            user_id: ID of the user requesting member list.

        Returns:
            Dict[str, Any]: Result with group members or error.
        """
        try:
            # Check if user is a member of the group
            membership = FamilyGroupMember.query.filter_by(
                family_group_id=group_id,
                user_id=user_id,
                is_active=True
            ).first()

            if not membership:
                return {
                    'success': False,
                    'error': 'You are not a member of this group'
                }

            # Get all active members
            members = FamilyGroupMember.query.filter_by(
                family_group_id=group_id,
                is_active=True
            ).all()

            members_data = [member.to_dict() for member in members]

            return {
                'success': True,
                'members': members_data,
                'count': len(members_data)
            }

        except Exception as e:
            return self.handle_service_error(e, 'get_family_group_members')

    def leave_family_group(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """Leave a family group.

        Args:
            group_id: ID of the family group.
            user_id: ID of the user leaving the group.

        Returns:
            Dict[str, Any]: Result with success status or error.
        """
        try:
            # Find the membership
            membership = FamilyGroupMember.query.filter_by(
                family_group_id=group_id,
                user_id=user_id,
                is_active=True
            ).first()

            if not membership:
                return {
                    'success': False,
                    'error': 'You are not a member of this group'
                }

            # Check if user is the admin
            if membership.role == 'admin':
                # Check if there are other members
                other_members = FamilyGroupMember.query.filter(
                    FamilyGroupMember.family_group_id == group_id,
                    FamilyGroupMember.user_id != user_id,
                    FamilyGroupMember.is_active
                ).count()

                if other_members > 0:
                    return {
                        'success': False,
                        'error': 'Admin cannot leave group with other members. Transfer admin role first.'
                    }

                # If no other members, deactivate the group
                group = membership.family_group
                group.is_active = False
                self.db_session.commit()

            # Deactivate the membership
            membership.is_active = False
            self.db_session.commit()

            self.logger.info(f"User {user_id} left family group {group_id}")

            return {
                'success': True,
                'message': 'Successfully left the family group'
            }

        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'leave_family_group')

    def regenerate_invite_code(self, group_id: int, user_id: int) -> Dict[str, Any]:
        """Regenerate invite code for a family group (admin only).

        Args:
            group_id: ID of the family group.
            user_id: ID of the user requesting regeneration.

        Returns:
            Dict[str, Any]: Result with new invite code or error.
        """
        try:
            # Check if user is admin of the group
            membership = FamilyGroupMember.query.filter_by(
                family_group_id=group_id,
                user_id=user_id,
                role='admin',
                is_active=True
            ).first()

            if not membership:
                return {
                    'success': False,
                    'error': 'Only group admins can regenerate invite codes'
                }

            # Regenerate invite code
            group = membership.family_group
            new_invite_code = group.generate_invite_code()
            self.db_session.commit()

            self.logger.info(f"Invite code regenerated for family group '{group.name}' by user {user_id}")

            return {
                'success': True,
                'message': 'Invite code regenerated successfully',
                'invite_code': new_invite_code
            }

        except Exception as e:
            self.rollback_session()
            return self.handle_service_error(e, 'regenerate_invite_code')
