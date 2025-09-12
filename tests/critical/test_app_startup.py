#!/usr/bin/env python3
"""Test Flask application startup."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app

def test_app_startup():
    """Test that the Flask application starts correctly."""
    with app.app_context():
        print("App context created successfully!")
        return True

if __name__ == '__main__':
    test_app_startup()
