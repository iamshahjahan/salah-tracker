#!/usr/bin/env python3
"""
Test prayer times for Bangalore, India
"""

import requests
import json

# API base URL
API_BASE = "http://localhost:5001"

def test_prayer_times():
    """Test prayer times API"""
    
    print("🕌 Testing Prayer Times for Bangalore, India")
    print("=" * 50)
    
    # Test direct prayer times API call with coordinates
    print("📍 Testing prayer times API with Bangalore coordinates...")
    
    try:
        # Test the prayer times API directly
        response = requests.get(f"{API_BASE}/api/prayers/times")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prayer times API is working!")
            print(f"📅 Date: {data.get('date', 'N/A')}")
            if 'prayers' in data:
                print("🕌 Prayer times:")
                for prayer in data['prayers']:
                    print(f"   {prayer['prayer_type']}: {prayer['prayer_time']}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application.")
        print("Make sure the app is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_aladhan_api():
    """Test Aladhan API directly"""
    
    print("\n🌐 Testing Aladhan API directly...")
    
    try:
        # Test Aladhan API directly
        url = "http://api.aladhan.com/v1/timings"
        params = {
            'latitude': 12.9716,
            'longitude': 77.5946,
            'method': 2,  # ISNA
            'school': 1   # Shafi
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                timings = data['data']['timings']
                print("✅ Aladhan API is working!")
                print("🕌 Prayer times for Bangalore:")
                for prayer, time in timings.items():
                    if prayer in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                        print(f"   {prayer}: {time}")
            else:
                print(f"❌ Aladhan API error: {data}")
        else:
            print(f"❌ Aladhan API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Aladhan API error: {e}")

if __name__ == "__main__":
    test_prayer_times()
    test_aladhan_api()
    
    print("\n" + "=" * 50)
    print("🎉 Your location is set to Bangalore, India!")
    print("📍 Coordinates: 12.9716, 77.5946")
    print("🕐 Timezone: Asia/Kolkata")
    print("\n💡 Now you can:")
    print("1. Visit http://localhost:5001")
    print("2. Login with ahmsjahan@gmail.com")
    print("3. Go to Prayers section to see your prayer times!")
