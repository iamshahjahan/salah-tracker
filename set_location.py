#!/usr/bin/env python3
"""
Set user location for Bangalore, India
This script helps you set your location coordinates in the database
"""

import requests
import json

# API base URL
API_BASE = "http://localhost:5001"

# Bangalore, India coordinates
BANGALORE_LAT = 12.9716
BANGALORE_LNG = 77.5946
BANGALORE_TIMEZONE = "Asia/Kolkata"

def set_user_location():
    """Set user location to Bangalore, India"""
    
    print("🌍 Setting location to Bangalore, India")
    print("=" * 50)
    
    # Get user input
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    # Login to get token
    print("\n🔐 Logging in...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print("✅ Login successful!")
            
            # Update profile with location
            print("\n📍 Setting location coordinates...")
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            location_data = {
                "location_lat": BANGALORE_LAT,
                "location_lng": BANGALORE_LNG,
                "timezone": BANGALORE_TIMEZONE
            }
            
            update_response = requests.put(
                f"{API_BASE}/api/auth/profile", 
                json=location_data, 
                headers=headers
            )
            
            if update_response.status_code == 200:
                print("✅ Location set successfully!")
                print(f"📍 Latitude: {BANGALORE_LAT}")
                print(f"📍 Longitude: {BANGALORE_LNG}")
                print(f"🕐 Timezone: {BANGALORE_TIMEZONE}")
                
                # Test prayer times
                print("\n🕌 Testing prayer times...")
                prayer_response = requests.get(
                    f"{API_BASE}/api/prayers/times",
                    headers=headers
                )
                
                if prayer_response.status_code == 200:
                    prayer_data = prayer_response.json()
                    print("✅ Prayer times loaded successfully!")
                    print(f"📅 Date: {prayer_data['date']}")
                    print("🕌 Today's prayers:")
                    for prayer in prayer_data['prayers']:
                        print(f"   {prayer['prayer_type']}: {prayer['prayer_time']}")
                else:
                    print(f"❌ Error loading prayer times: {prayer_response.status_code}")
                    print(prayer_response.text)
                    
            else:
                print(f"❌ Error updating profile: {update_response.status_code}")
                print(update_response.text)
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application.")
        print("Make sure the app is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("SalahReminders - Location Setup for Bangalore, India")
    print("=" * 60)
    print(f"📍 Setting coordinates: {BANGALORE_LAT}, {BANGALORE_LNG}")
    print(f"🕐 Timezone: {BANGALORE_TIMEZONE}")
    print()
    
    set_user_location()
