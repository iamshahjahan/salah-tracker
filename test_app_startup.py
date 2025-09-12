#!/usr/bin/env python3
"""Test Flask application startup."""

from main import app

def test_app_startup():
    """Test that the Flask application starts correctly."""
    with app.app_context():
        print("App context created successfully!")
        return True

if __name__ == '__main__':
    test_app_startup()
