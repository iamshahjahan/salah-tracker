"""Inspirational Content API routes.

This module defines API endpoints for accessing Quranic verses and Hadith
for use in prayer reminders and notifications.
"""


from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models.inspirational_content import Hadith, QuranicVerse

# Create blueprint
inspirational_bp = Blueprint('inspirational', __name__)


@inspirational_bp.route('/verse/random', methods=['GET'])
@jwt_required()
def get_random_verse():
    """Get a random Quranic verse."""
    try:
        category = request.args.get('category', None)

        verse = QuranicVerse.get_random_verse(category)

        if verse:
            return jsonify({
                'success': True,
                'verse': verse.to_dict()
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

        hadith = Hadith.get_random_hadith(category)

        if hadith:
            return jsonify({
                'success': True,
                'hadith': hadith.to_dict()
            }), 200
        return jsonify({
            'success': False,
            'error': 'No Hadith found'
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/verse/<int:verse_id>', methods=['GET'])
@jwt_required()
def get_verse_by_id(verse_id):
    """Get a specific Quranic verse by ID."""
    try:
        verse = QuranicVerse.query.get(verse_id)

        if verse and verse.is_active:
            return jsonify({
                'success': True,
                'verse': verse.to_dict()
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
        hadith = Hadith.query.get(hadith_id)

        if hadith and hadith.is_active:
            return jsonify({
                'success': True,
                'hadith': hadith.to_dict()
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
    """Get a list of Quranic verses with optional filtering."""
    try:
        category = request.args.get('category', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = QuranicVerse.query.filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)

        verses = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'success': True,
            'verses': [verse.to_dict() for verse in verses.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': verses.total,
                'pages': verses.pages,
                'has_next': verses.has_next,
                'has_prev': verses.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/hadiths', methods=['GET'])
@jwt_required()
def get_hadiths():
    """Get a list of Hadith with optional filtering."""
    try:
        category = request.args.get('category', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = Hadith.query.filter_by(is_active=True)

        if category:
            query = query.filter_by(category=category)

        hadiths = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'success': True,
            'hadiths': [hadith.to_dict() for hadith in hadiths.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': hadiths.total,
                'pages': hadiths.pages,
                'has_next': hadiths.has_next,
                'has_prev': hadiths.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inspirational_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get available categories for verses and Hadith."""
    try:
        from config.database import db

        # Get unique categories from verses
        verse_categories = db.session.query(QuranicVerse.category).filter(
            QuranicVerse.is_active,
            QuranicVerse.category.isnot(None)
        ).distinct().all()

        # Get unique categories from Hadith
        hadith_categories = db.session.query(Hadith.category).filter(
            Hadith.is_active,
            Hadith.category.isnot(None)
        ).distinct().all()

        # Combine and deduplicate categories
        all_categories = set()
        for category in verse_categories:
            if category[0]:
                all_categories.add(category[0])
        for category in hadith_categories:
            if category[0]:
                all_categories.add(category[0])

        return jsonify({
            'success': True,
            'categories': sorted(all_categories)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
