"""Inspirational Content API routes.

This module defines API endpoints for accessing Quranic verses and Hadith
from JSON files for use in prayer reminders and notifications.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.inspirational_service import InspirationalService
from app.config.settings import get_config

# Create blueprint
inspirational_bp = Blueprint('inspirational', __name__)


@inspirational_bp.route('/verse/random', methods=['GET'])
@jwt_required()
def get_random_verse():
    """Get a random Quranic verse."""
    try:
        category = request.args.get('category', None)
        
        config = get_config()
        inspirational_service = InspirationalService(config)
        verse = inspirational_service.get_random_verse(category)

        if verse:
            return jsonify({
                'success': True,
                'verse': verse
            }), 200
        return jsonify({
            'success': False,
            'error': 'No verses found'
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/hadith/random', methods=['GET'])
@jwt_required()
def get_random_hadith():
    """Get a random Hadith."""
    try:
        category = request.args.get('category', None)
        
        config = get_config()
        inspirational_service = InspirationalService(config)
        hadith = inspirational_service.get_random_hadith(category)

        if hadith:
            return jsonify({
                'success': True,
                'hadith': hadith
            }), 200
        return jsonify({
            'success': False,
            'error': 'No hadith found'
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/verse/<int:verse_id>', methods=['GET'])
@jwt_required()
def get_verse_by_id(verse_id):
    """Get a specific Quranic verse by ID."""
    try:
        config = get_config()
        inspirational_service = InspirationalService(config)
        verse = inspirational_service.get_verse_by_id(verse_id)

        if verse:
            return jsonify({
                'success': True,
                'verse': verse
            }), 200
        return jsonify({
            'success': False,
            'error': 'Verse not found'
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/hadith/<int:hadith_id>', methods=['GET'])
@jwt_required()
def get_hadith_by_id(hadith_id):
    """Get a specific Hadith by ID."""
    try:
        config = get_config()
        inspirational_service = InspirationalService(config)
        hadith = inspirational_service.get_hadith_by_id(hadith_id)

        if hadith:
            return jsonify({
                'success': True,
                'hadith': hadith
            }), 200
        return jsonify({
            'success': False,
            'error': 'Hadith not found'
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/verses', methods=['GET'])
@jwt_required()
def get_verses():
    """Get Quranic verses with optional filtering."""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        config = get_config()
        inspirational_service = InspirationalService(config)
        
        if category:
            verses = inspirational_service.get_verses_by_category(category, limit)
        else:
            # Get all verses from the content and apply limit if specified
            content = inspirational_service._load_content()
            verses = content.get('quranic_verses', [])
            if limit:
                verses = verses[:limit]

        return jsonify({
            'success': True,
            'verses': verses,
            'total': len(verses)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/hadiths', methods=['GET'])
@jwt_required()
def get_hadiths():
    """Get Hadith with optional filtering."""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        config = get_config()
        inspirational_service = InspirationalService(config)
        
        if category:
            hadiths = inspirational_service.get_hadith_by_category(category, limit)
        else:
            # Get all hadith from the content and apply limit if specified
            content = inspirational_service._load_content()
            hadiths = content.get('hadith', [])
            if limit:
                hadiths = hadiths[:limit]

        return jsonify({
            'success': True,
            'hadiths': hadiths,
            'total': len(hadiths)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get available categories for verses and Hadith."""
    try:
        config = get_config()
        inspirational_service = InspirationalService(config)
        categories = inspirational_service.get_available_categories()

        return jsonify({
            'success': True,
            'categories': categories
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/reload', methods=['POST'])
@jwt_required()
def reload_content():
    """Reload inspirational content from JSON file."""
    try:
        config = get_config()
        inspirational_service = InspirationalService(config)
        success = inspirational_service.reload_content()

        if success:
            return jsonify({
                'success': True,
                'message': 'Content reloaded successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reload content'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500