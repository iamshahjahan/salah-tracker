#!/usr/bin/env python3
"""Test notification service initialization."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app
from app.services.notification_service import NotificationService

def test_notification_service():
    """Test that notification service can be initialized."""
    with app.app_context():
        service = NotificationService()
        print("Notification service initialized successfully!")
        return True

if __name__ == '__main__':
    test_notification_service()
