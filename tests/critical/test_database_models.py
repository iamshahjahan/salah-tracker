#!/usr/bin/env python3
"""Test database models accessibility."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app
from app.models import User, Prayer, PrayerCompletion

def test_database_models():
    """Test that database models are accessible."""
    with app.app_context():
        print("Database models accessible!")
        return True

if __name__ == '__main__':
    test_database_models()
