#!/usr/bin/env python3
"""
Pre-deployment test runner for Salah Tracker.

This script runs all critical tests before deployment to ensure
the application is working correctly.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print("Output:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False

def test_python_syntax():
    """Test Python syntax in all Python files."""
    return run_command(
        "find . -name '*.py' -not -path './venv/*' -not -path './.venv/*' -exec python3 -m py_compile {} \\;",
        "Python Syntax Check"
    )

def test_imports():
    """Test that all imports work correctly."""
    return run_command(
        "python3 -c 'from main import app; from app.models import *; from app.services import *; from app.routes import *; print(\"All imports successful!\")'",
        "Import Test"
    )

def test_application_startup():
    """Test that the Flask application starts correctly."""
    return run_command(
        "python3 -c 'from main import app; with app.app_context(): print(\"App context created successfully!\")'",
        "Application Startup Test"
    )

def test_database_models():
    """Test that database models are accessible."""
    return run_command(
        "python3 -c 'from main import app; from app.models import User, Prayer, PrayerCompletion; with app.app_context(): print(\"Database models accessible!\")'",
        "Database Models Test"
    )

def test_email_notifications():
    """Test email notification functionality."""
    return run_command(
        "python3 -m pytest app/tests/test_email_notifications.py -v",
        "Email Notifications Test"
    )

def test_auth_service():
    """Test authentication service."""
    return run_command(
        "python3 -m pytest app/tests/test_auth_service.py -v",
        "Authentication Service Test"
    )

def test_prayer_service():
    """Test prayer service."""
    return run_command(
        "python3 -m pytest app/tests/test_prayer_service.py -v",
        "Prayer Service Test"
    )

def test_validators():
    """Test validation functions."""
    return run_command(
        "python3 -m pytest app/tests/test_validators.py -v",
        "Validators Test"
    )

def test_celery_configuration():
    """Test Celery configuration."""
    return run_command(
        "python3 -c 'from celery_config import celery_app; print(\"Celery configuration loaded successfully!\")'",
        "Celery Configuration Test"
    )

def test_email_templates():
    """Test email template generation."""
    return run_command(
        "python3 -c 'from app.services.email_templates import get_prayer_name_arabic, get_prayer_name_english; print(f\"Arabic: {get_prayer_name_arabic(\"FAJR\")}\"); print(f\"English: {get_prayer_name_english(\"FAJR\")}\")'",
        "Email Templates Test"
    )

def test_notification_service():
    """Test notification service initialization."""
    return run_command(
        "python3 -c 'from main import app; from app.services.notification_service import NotificationService; with app.app_context(): ns = NotificationService(); print(\"Notification service initialized successfully!\")'",
        "Notification Service Test"
    )

def main():
    """Run all pre-deployment tests."""
    print("🚀 Salah Tracker - Pre-Deployment Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List of all tests to run
    tests = [
        ("Python Syntax", test_python_syntax),
        ("Import Test", test_imports),
        ("Application Startup", test_application_startup),
        ("Database Models", test_database_models),
        ("Email Templates", test_email_templates),
        ("Notification Service", test_notification_service),
        ("Celery Configuration", test_celery_configuration),
        ("Email Notifications", test_email_notifications),
        ("Authentication Service", test_auth_service),
        ("Prayer Service", test_prayer_service),
        ("Validators", test_validators),
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        duration = end_time - start_time
        results.append((test_name, success, duration))
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {sum(r[2] for r in results):.2f} seconds")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name} ({duration:.2f}s)")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Ready for deployment.")
        return 0
    else:
        print(f"\n💥 {failed} TEST(S) FAILED! Do not deploy until fixed.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
