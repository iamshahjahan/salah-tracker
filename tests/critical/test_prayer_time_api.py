#!/usr/bin/env python3
"""Test external prayer time API connectivity."""

import requests

def test_prayer_time_api():
    """Test that the Aladhan API is accessible."""
    try:
        # Test the Aladhan API
        url = "http://api.aladhan.com/v1/calendar/2025/9"
        params = {
            'latitude': 12.9716,
            'longitude': 77.5946,
            'method': 2
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                print("Aladhan API is accessible and returning data")
                return True
            else:
                print("API returned empty data")
                return False
        else:
            print(f"API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == '__main__':
    test_prayer_time_api()
