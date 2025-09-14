#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all comprehensive tests to verify complete application functionality.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Exit Code: {result.returncode}")
        print(f"Execution Time: {execution_time:.2f} seconds")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return {
            'success': result.returncode == 0,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'execution_time': execution_time
        }
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Command exceeded 5 minutes")
        return {
            'success': False,
            'exit_code': -1,
            'stdout': '',
            'stderr': 'Command timed out after 5 minutes',
            'execution_time': 300
        }
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            'success': False,
            'exit_code': -1,
            'stdout': '',
            'stderr': str(e),
            'execution_time': 0
        }

def main():
    """Main test runner"""
    print("🚀 Salah Tracker - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test categories
    test_categories = [
        {
            'name': 'API Endpoints',
            'file': 'test_api_endpoints.py',
            'description': 'Comprehensive API endpoint testing'
        },
        {
            'name': 'Database Operations',
            'file': 'test_database_operations.py',
            'description': 'Database operations and data integrity testing'
        },
        {
            'name': 'Service Layer',
            'file': 'test_service_layer.py',
            'description': 'Business logic and service layer testing'
        },
        {
            'name': 'Celery Tasks',
            'file': 'test_celery_tasks.py',
            'description': 'Background task processing testing'
        },
        {
            'name': 'Frontend Functionality',
            'file': 'test_frontend_functionality.py',
            'description': 'Frontend integration and functionality testing'
        }
    ]
    
    results = []
    total_tests = len(test_categories)
    passed_tests = 0
    
    # Run each test category
    for i, category in enumerate(test_categories, 1):
        print(f"\n📋 Test Category {i}/{total_tests}: {category['name']}")
        print(f"Description: {category['description']}")
        
        test_file = os.path.join(os.path.dirname(__file__), category['file'])
        command = f"python3 -m pytest {test_file} -v --tb=short"
        
        result = run_command(command, category['name'])
        result['category'] = category['name']
        result['description'] = category['description']
        results.append(result)
        
        if result['success']:
            passed_tests += 1
            print(f"✅ {category['name']} - PASSED")
        else:
            print(f"❌ {category['name']} - FAILED")
    
    # Run integration tests
    print(f"\n📋 Integration Tests")
    integration_command = "python3 -m pytest tests/comprehensive/ -k 'integration' -v --tb=short"
    integration_result = run_command(integration_command, "Integration Tests")
    integration_result['category'] = 'Integration Tests'
    integration_result['description'] = 'Cross-component integration testing'
    results.append(integration_result)
    
    if integration_result['success']:
        passed_tests += 1
        print("✅ Integration Tests - PASSED")
    else:
        print("❌ Integration Tests - FAILED")
    
    # Run performance tests
    print(f"\n📋 Performance Tests")
    performance_command = "python3 -m pytest tests/comprehensive/ -k 'performance' -v --tb=short"
    performance_result = run_command(performance_command, "Performance Tests")
    performance_result['category'] = 'Performance Tests'
    performance_result['description'] = 'Performance and load testing'
    results.append(performance_result)
    
    if performance_result['success']:
        passed_tests += 1
        print("✅ Performance Tests - PASSED")
    else:
        print("❌ Performance Tests - FAILED")
    
    # Run security tests
    print(f"\n📋 Security Tests")
    security_command = "python3 -m pytest tests/comprehensive/ -k 'security' -v --tb=short"
    security_result = run_command(security_command, "Security Tests")
    security_result['category'] = 'Security Tests'
    security_result['description'] = 'Security vulnerability testing'
    results.append(security_result)
    
    if security_result['success']:
        passed_tests += 1
        print("✅ Security Tests - PASSED")
    else:
        print("❌ Security Tests - FAILED")
    
    # Calculate total execution time
    total_execution_time = sum(result['execution_time'] for result in results)
    total_tests = len(results)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Categories: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"⏱️  Total Time: {total_execution_time:.2f} seconds")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {status} {result['category']} ({result['execution_time']:.2f}s)")
        if not result['success'] and result['stderr']:
            print(f"    Error: {result['stderr'][:100]}...")
    
    # Print recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Application is ready for production.")
        print("✅ All core functionality is working correctly")
        print("✅ Database operations are stable")
        print("✅ API endpoints are functioning properly")
        print("✅ Background tasks are processing correctly")
        print("✅ Frontend integration is working")
        print("✅ Security measures are in place")
        print("✅ Performance is within acceptable limits")
    else:
        failed_tests = [r for r in results if not r['success']]
        print(f"⚠️  {len(failed_tests)} test categories failed. Please review:")
        for result in failed_tests:
            print(f"   - {result['category']}: {result['description']}")
        print("\n🔧 Next Steps:")
        print("   1. Review failed test outputs above")
        print("   2. Fix identified issues")
        print("   3. Re-run specific test categories")
        print("   4. Ensure all functionality works before deployment")
    
    # Exit with appropriate code
    if passed_tests == total_tests:
        print(f"\n🎉 COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"\n❌ COMPREHENSIVE TESTING FAILED - {total_tests - passed_tests} categories failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
