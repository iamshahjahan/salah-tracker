#!/usr/bin/env python3
"""Test email notification functionality without database."""

from datetime import datetime, time, date
from app.services.email_templates import get_prayer_name_arabic, get_prayer_name_english, get_prayer_reminder_template
from app.models.user import User

def test_email_notifications_unit():
    """Test email notification functionality without database."""
    # Test prayer name functions
    assert get_prayer_name_arabic('fajr') == 'الفجر'
    assert get_prayer_name_english('fajr') == 'Fajr'
    print("Prayer name functions work correctly")

    # Test template generation
    user = User()
    user.language = 'en'
    user.first_name = 'Test'
    user.last_name = 'User'

    prayer_time = datetime.combine(date.today(), time(5, 30))
    template = get_prayer_reminder_template(user, 'fajr', prayer_time, None, None, 'test-link')
    assert 'Fajr' in template
    assert '05:30' in template
    print("Email template generation works correctly")

    print("All email notification unit tests passed!")
    return True

if __name__ == '__main__':
    test_email_notifications_unit()
