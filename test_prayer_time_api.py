#!/usr/bin/env python3
"""Test prayer time API functionality."""

import requests
from datetime import date

def test_prayer_time_api():
    """Test prayer time API functionality."""
    # Test Aladhan API
    today = date.today()
    url = f'https://api.aladhan.com/v1/calendar/{today.year}/{today.month}'
    params = {'latitude': 12.9716, 'longitude': 77.5946, 'method': 2, 'school': 1}

    response = requests.get(url, params=params, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data.get('status') == 'OK'
    assert 'data' in data
    print("Aladhan API is accessible and returning data")
    return True

if __name__ == '__main__':
    test_prayer_time_api()
