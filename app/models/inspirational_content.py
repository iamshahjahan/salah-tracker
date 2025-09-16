"""Inspirational content model for Quranic verses and Hadith.

This module defines models for storing and managing Quranic verses
and Hadith that can be used in prayer reminders and notifications.
"""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from config.database import db


class QuranicVerse(db.Model):
    """Model for Quranic verses."""

    __tablename__ = 'quranic_verses'

    id = db.Column(db.Integer, primary_key=True)
    surah_number = db.Column(db.Integer, nullable=False)
    surah_name_arabic = db.Column(db.String(100), nullable=False)
    surah_name_english = db.Column(db.String(100), nullable=False)
    verse_number = db.Column(db.Integer, nullable=False)
    arabic_text = db.Column(db.Text, nullable=False)
    english_translation = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # prayer, patience, guidance, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Quranic verse to dictionary."""
        return {
            'id': self.id,
            'surah_number': self.surah_number,
            'surah_name_arabic': self.surah_name_arabic,
            'surah_name_english': self.surah_name_english,
            'verse_number': self.verse_number,
            'arabic_text': self.arabic_text,
            'english_translation': self.english_translation,
            'category': self.category,
            'reference': f"{self.surah_name_english} {self.surah_number}:{self.verse_number}"
        }

    @classmethod
    def get_random_verse(cls, category: Optional[str] = None) -> 'QuranicVerse':
        """Get a random Quranic verse, optionally filtered by category."""
        query = cls.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        verses = query.all()
        return random.choice(verses) if verses else None

    def __repr__(self):
        return f'<QuranicVerse {self.surah_name_english} {self.surah_number}:{self.verse_number}>'


class Hadith(db.Model):
    """Model for Hadith."""

    __tablename__ = 'hadith'

    id = db.Column(db.Integer, primary_key=True)
    collection = db.Column(db.String(100), nullable=False)  # Bukhari, Muslim, etc.
    hadith_number = db.Column(db.String(50), nullable=True)
    arabic_text = db.Column(db.Text, nullable=False)
    english_translation = db.Column(db.Text, nullable=False)
    narrator = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(50), nullable=True)  # prayer, patience, guidance, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Hadith to dictionary."""
        return {
            'id': self.id,
            'collection': self.collection,
            'hadith_number': self.hadith_number,
            'arabic_text': self.arabic_text,
            'english_translation': self.english_translation,
            'narrator': self.narrator,
            'category': self.category,
            'reference': f"{self.collection} {self.hadith_number}" if self.hadith_number else self.collection
        }

    @classmethod
    def get_random_hadith(cls, category: Optional[str] = None) -> 'Hadith':
        """Get a random Hadith, optionally filtered by category."""
        query = cls.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        hadiths = query.all()
        return random.choice(hadiths) if hadiths else None

    def __repr__(self):
        return f'<Hadith {self.collection} {self.hadith_number}>'
