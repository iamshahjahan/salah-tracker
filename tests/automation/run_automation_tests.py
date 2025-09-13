#!/usr/bin/env python3
"""Main runner for automation tests."""

import unittest
import sys
import os
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def run_automation_tests(parallel=False, max_workers=3):
    """Run all automation tests."""
    if parallel:
        # Import and use parallel runner
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from run_automation_tests_parallel import run_automation_tests_parallel
        return run_automation_tests_parallel(max_workers)
    
    print("🚀 Salah Tracker - Sequential Automation Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create screenshots directory
    os.makedirs("screenshots", exist_ok=True)
    
    # Test modules to run
    test_modules = [
        'tests.automation.test_website_accessibility',
        'tests.automation.test_basic_selenium',
        'tests.automation.test_user_registration',
        'tests.automation.test_otp_functionality', 
        'tests.automation.test_reminder_functionality',
        'tests.automation.test_dashboard',
        'tests.automation.test_prayer_completion'
    ]
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            print(f"✅ Loaded test module: {module_name}")
        except Exception as e:
            print(f"❌ Failed to load test module {module_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 AUTOMATION TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"⏱️  Total Time: {end_time - start_time:.2f} seconds")
    
    print("\n📋 DETAILED RESULTS:")
    for test, traceback in result.failures:
        print(f"  ❌ FAIL {test}")
    for test, traceback in result.errors:
        print(f"  💥 ERROR {test}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 ALL AUTOMATION TESTS PASSED! Ready for production.")
        return True
    else:
        print(f"\n💥 {failures + errors} AUTOMATION TEST(S) FAILED! Do not deploy until fixed.")
        return False

if __name__ == '__main__':
    # Check for parallel execution flag
    parallel = '--parallel' in sys.argv or os.getenv('PARALLEL_TESTS', 'false').lower() == 'true'
    max_workers = 3
    
    # Parse max workers from command line
    for arg in sys.argv:
        if arg.startswith('--workers='):
            max_workers = int(arg.split('=')[1])
    
    success = run_automation_tests(parallel=parallel, max_workers=max_workers)
    sys.exit(0 if success else 1)
