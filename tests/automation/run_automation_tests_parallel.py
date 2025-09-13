#!/usr/bin/env python3
"""Parallel runner for automation tests."""

import unittest
import sys
import os
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class ParallelTestResult:
    """Custom test result collector for parallel execution."""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.successes = []
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def add_result(self, result):
        """Add a test result."""
        with self.lock:
            self.tests_run += result.testsRun
            self.failures.extend(result.failures)
            self.errors.extend(result.errors)
            if hasattr(result, 'skipped'):
                self.skipped.extend(result.skipped)
            # Calculate successes
            successes = result.testsRun - len(result.failures) - len(result.errors)
            if hasattr(result, 'skipped'):
                successes -= len(result.skipped)
            self.successes.extend([f"Test {i}" for i in range(successes)])
    
    def get_summary(self):
        """Get test summary."""
        end_time = time.time()
        total_tests = self.tests_run
        failures = len(self.failures)
        errors = len(self.errors)
        skipped = len(self.skipped)
        passed = total_tests - failures - errors - skipped
        
        return {
            'total_tests': total_tests,
            'passed': passed,
            'failures': failures,
            'errors': errors,
            'skipped': skipped,
            'duration': end_time - self.start_time
        }

def run_test_module(module_name, max_workers=1):
    """Run a single test module."""
    try:
        # Create a separate test suite for this module
        loader = unittest.TestLoader()
        module = __import__(module_name, fromlist=[''])
        suite = loader.loadTestsFromModule(module)
        
        # Create a test runner
        runner = unittest.TextTestRunner(
            verbosity=0,  # Reduced verbosity for parallel execution
            stream=open(os.devnull, 'w'),  # Suppress output during parallel execution
            descriptions=False,
            failfast=False
        )
        
        # Run the tests
        result = runner.run(suite)
        
        return {
            'module': module_name,
            'result': result,
            'success': len(result.failures) == 0 and len(result.errors) == 0
        }
        
    except Exception as e:
        return {
            'module': module_name,
            'result': None,
            'success': False,
            'error': str(e)
        }

def run_automation_tests_parallel(max_workers=3):
    """Run all automation tests in parallel."""
    print("🚀 Salah Tracker - Parallel Automation Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Max Workers: {max_workers}")
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
    
    # Create parallel test result collector
    parallel_result = ParallelTestResult()
    
    # Run tests in parallel
    print(f"🔄 Running {len(test_modules)} test modules in parallel...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all test modules
        future_to_module = {
            executor.submit(run_test_module, module_name): module_name 
            for module_name in test_modules
        }
        
        # Collect results as they complete
        completed_tests = []
        for future in as_completed(future_to_module):
            module_name = future_to_module[future]
            try:
                result = future.result()
                completed_tests.append(result)
                
                if result['success']:
                    print(f"✅ {module_name} - PASSED")
                else:
                    print(f"❌ {module_name} - FAILED")
                    if 'error' in result:
                        print(f"   Error: {result['error']}")
                
                # Add to parallel result
                if result['result']:
                    parallel_result.add_result(result['result'])
                    
            except Exception as e:
                print(f"💥 {module_name} - ERROR: {e}")
                completed_tests.append({
                    'module': module_name,
                    'result': None,
                    'success': False,
                    'error': str(e)
                })
    
    # Print detailed results
    print("\n" + "=" * 60)
    print("📊 PARALLEL AUTOMATION TEST SUMMARY")
    print("=" * 60)
    
    summary = parallel_result.get_summary()
    
    print(f"Total Tests: {summary['total_tests']}")
    print(f"✅ Passed: {summary['passed']}")
    print(f"❌ Failed: {summary['failures']}")
    print(f"💥 Errors: {summary['errors']}")
    print(f"⏭️  Skipped: {summary['skipped']}")
    print(f"⏱️  Total Time: {summary['duration']:.2f} seconds")
    
    # Print module-level results
    print("\n📋 MODULE RESULTS:")
    for test_result in completed_tests:
        status = "✅ PASSED" if test_result['success'] else "❌ FAILED"
        print(f"  {status} - {test_result['module']}")
        if 'error' in test_result:
            print(f"    Error: {test_result['error']}")
    
    # Print detailed failures and errors
    if parallel_result.failures or parallel_result.errors:
        print("\n📋 DETAILED FAILURES:")
        for test, traceback in parallel_result.failures:
            print(f"  ❌ FAIL {test}")
        for test, traceback in parallel_result.errors:
            print(f"  💥 ERROR {test}")
    
    # Final result
    if summary['failures'] == 0 and summary['errors'] == 0:
        print("\n🎉 ALL PARALLEL AUTOMATION TESTS PASSED! Ready for production.")
        return True
    else:
        print(f"\n💥 {summary['failures'] + summary['errors']} AUTOMATION TEST(S) FAILED! Do not deploy until fixed.")
        return False

if __name__ == '__main__':
    # Allow customization of max workers
    max_workers = int(os.getenv('MAX_WORKERS', '3'))
    success = run_automation_tests_parallel(max_workers)
    sys.exit(0 if success else 1)
