#!/usr/bin/env python3
"""Test notification service initialization."""

from main import app
from app.services.notification_service import NotificationService

def test_notification_service():
    """Test notification service initialization."""
    with app.app_context():
        ns = NotificationService()
        print("Notification service initialized successfully!")
        return True

if __name__ == '__main__':
    test_notification_service()
