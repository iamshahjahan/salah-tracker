#!/usr/bin/env python3
"""Unit tests for email notification components."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.email_templates import get_prayer_name_arabic, get_prayer_name_english

def test_email_notifications_unit():
    """Test email notification unit functions."""
    # Test Arabic prayer names
    assert get_prayer_name_arabic('fajr') == 'الفجر'
    assert get_prayer_name_arabic('dhuhr') == 'الظهر'
    assert get_prayer_name_arabic('asr') == 'العصر'
    assert get_prayer_name_arabic('maghrib') == 'المغرب'
    assert get_prayer_name_arabic('isha') == 'العشاء'
    
    # Test English prayer names
    assert get_prayer_name_english('fajr') == 'Fajr'
    assert get_prayer_name_english('dhuhr') == 'Dhuhr'
    assert get_prayer_name_english('asr') == 'Asr'
    assert get_prayer_name_english('maghrib') == 'Maghrib'
    assert get_prayer_name_english('isha') == 'Isha'
    
    print("All email notification unit tests passed!")
    return True

if __name__ == '__main__':
    test_email_notifications_unit()
