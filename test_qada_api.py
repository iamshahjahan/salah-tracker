#!/usr/bin/env python3

import requests
import json
from datetime import datetime, date

# Test the Qada API functionality
BASE_URL = "http://localhost:5001"

def test_qada_api():
    # First, login to get a token
    login_data = {
        "username": "khsaheli195@gmail.com",
        "password": "khankhan"
    }
    
    print("1. Logging in...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Test today's prayers
    print("\n2. Testing today's prayers...")
    response = requests.get(f"{BASE_URL}/api/prayers/times", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Today's prayers: {len(data['prayers'])} prayers")
        for prayer in data['prayers']:
            print(f"  {prayer['prayer_type']}: {prayer['prayer_time']} - {prayer.get('completed', False)} - can_mark_qada: {prayer.get('can_mark_qada', False)}")
    else:
        print(f"Failed to get today's prayers: {response.text}")
    
    # Test a specific past date (September 10, 2025)
    print("\n3. Testing September 10, 2025 prayers...")
    response = requests.get(f"{BASE_URL}/api/prayers/times/2025-09-10", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"September 10 prayers: {len(data['prayers'])} prayers")
        for prayer in data['prayers']:
            print(f"  {prayer['prayer_type']}: {prayer['prayer_time']} - completed: {prayer.get('completed', False)} - can_mark_qada: {prayer.get('can_mark_qada', False)}")
            if prayer.get('completion'):
                print(f"    completion: {prayer['completion']}")
    else:
        print(f"Failed to get September 10 prayers: {response.text}")

if __name__ == "__main__":
    test_qada_api()
