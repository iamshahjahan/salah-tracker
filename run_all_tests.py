#!/usr/bin/env python3
"""Comprehensive test runner for all test suites."""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print("Output:", result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
        
        print(f"⏱️  Time: {end_time - start_time:.2f}s")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Command took too long")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def check_automation_dependencies():
    """Check if automation test dependencies are installed."""
    try:
        import selenium
        import webdriver_manager
        import requests
        return True
    except ImportError:
        print("⚠️ Automation test dependencies not installed.")
        print("Install with: pip install -r requirements-automation.txt")
        return False

def main():
    """Run all test suites."""
    print("🚀 Salah Tracker - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # 1. Critical Tests
    print("\n🔍 Running Critical Tests...")
    critical_success = run_command("python3 run_critical_tests.py", "Critical Tests")
    results.append(("Critical Tests", critical_success))
    
    # 2. Unit Tests (if available)
    print("\n🧪 Running Unit Tests...")
    unit_success = run_command("python3 -m pytest app/tests/ -v", "Unit Tests")
    results.append(("Unit Tests", unit_success))
    
    # 3. Automation Tests (if dependencies available)
    print("\n🤖 Running Automation Tests...")
    if check_automation_dependencies():
        # Check for parallel execution flag
        parallel = '--parallel' in sys.argv or os.getenv('PARALLEL_TESTS', 'false').lower() == 'true'
        max_workers = 3
        
        # Parse max workers from command line
        for arg in sys.argv:
            if arg.startswith('--workers='):
                max_workers = int(arg.split('=')[1])
        
        if parallel:
            automation_success = run_command(f"python3 tests/automation/run_automation_tests.py --parallel --workers={max_workers}", f"Parallel Automation Tests (Workers: {max_workers})")
        else:
            automation_success = run_command("python3 tests/automation/run_automation_tests.py", "Sequential Automation Tests")
        results.append(("Automation Tests", automation_success))
    else:
        print("⏭️  Skipping automation tests - dependencies not installed")
        results.append(("Automation Tests", True))  # Don't fail build for missing deps
    
    # 4. Integration Tests (if available)
    print("\n🔗 Running Integration Tests...")
    integration_success = run_command("python3 -m pytest tests/integration/ -v", "Integration Tests")
    results.append(("Integration Tests", integration_success))
    
    # 5. Security Tests (if available)
    print("\n🔒 Running Security Tests...")
    security_success = run_command("python3 -m pytest tests/security/ -v", "Security Tests")
    results.append(("Security Tests", security_success))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    print("\n📋 DETAILED RESULTS:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TEST SUITES PASSED! Ready for production deployment.")
        return True
    else:
        print(f"\n💥 {failed_tests} TEST SUITE(S) FAILED! Do not deploy until fixed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
