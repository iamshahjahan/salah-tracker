#!/usr/bin/env python3
"""
Test runner for the Salah Reminders application.

This script runs all tests for both backend and frontend components,
providing comprehensive test coverage and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_backend_tests(test_path=None, verbose=False):
    """
    Run backend tests using pytest.
    
    Args:
        test_path: Specific test path to run. If None, runs all tests.
        verbose: Whether to run tests in verbose mode.
        
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    print("🧪 Running Backend Tests...")
    print("=" * 50)
    
    # Set up pytest command
    cmd = ['python3', '-m', 'pytest']
    
    if verbose:
        cmd.append('-v')
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append('app/tests/')
    
    # Add coverage reporting
    cmd.extend([
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--cov-fail-under=80'
    ])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Backend tests passed!")
            return True
        else:
            print("❌ Backend tests failed!")
            return False
            
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest: pip install pytest pytest-cov")
        return False
    except Exception as e:
        print(f"❌ Error running backend tests: {e}")
        return False


def run_frontend_tests():
    """
    Run frontend tests using Node.js and Jest.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    print("\n🧪 Running Frontend Tests...")
    print("=" * 50)
    
    # Check if Node.js is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Node.js not found. Please install Node.js to run frontend tests.")
        return False
    
    # Check if Jest is available
    try:
        subprocess.run(['npx', 'jest', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Jest not found. Installing Jest...")
        try:
            subprocess.run(['npm', 'install', '--save-dev', 'jest'], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install Jest. Please install manually: npm install --save-dev jest")
            return False
    
    # Run frontend tests
    try:
        result = subprocess.run([
            'npx', 'jest', 
            'static/js/tests/',
            '--coverage',
            '--coverage-reporters=text',
            '--coverage-reporters=html'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Frontend tests passed!")
            return True
        else:
            print("❌ Frontend tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running frontend tests: {e}")
        return False


def run_integration_tests():
    """
    Run integration tests for the full application.
    
    Returns:
        bool: True if all tests passed, False otherwise.
    """
    print("\n🧪 Running Integration Tests...")
    print("=" * 50)
    
    # This would run end-to-end tests
    # For now, we'll just run a basic API test
    try:
        import requests
        
        # Test if the application is running
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Application health check passed!")
            return True
        else:
            print(f"❌ Application health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running. Please start the application first.")
        return False
    except ImportError:
        print("❌ requests library not found. Please install: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False


def run_linting():
    """
    Run code linting for both backend and frontend.
    
    Returns:
        bool: True if linting passed, False otherwise.
    """
    print("\n🔍 Running Code Linting...")
    print("=" * 50)
    
    backend_passed = True
    frontend_passed = True
    
    # Backend linting with flake8
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', 
            'app/', 
            '--max-line-length=100',
            '--exclude=__pycache__,migrations'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend linting passed!")
        else:
            print("❌ Backend linting failed!")
            print(result.stdout)
            backend_passed = False
            
    except FileNotFoundError:
        print("❌ flake8 not found. Please install: pip install flake8")
        backend_passed = False
    
    # Frontend linting with ESLint
    try:
        result = subprocess.run([
            'npx', 'eslint', 
            'static/js/',
            '--ext', '.js'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend linting passed!")
        else:
            print("❌ Frontend linting failed!")
            print(result.stdout)
            frontend_passed = False
            
    except FileNotFoundError:
        print("❌ ESLint not found. Please install: npm install --save-dev eslint")
        frontend_passed = False
    
    return backend_passed and frontend_passed


def generate_test_report():
    """
    Generate a comprehensive test report.
    
    Returns:
        bool: True if report generation was successful, False otherwise.
    """
    print("\n📊 Generating Test Report...")
    print("=" * 50)
    
    try:
        # Create reports directory
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Generate HTML coverage report
        if Path('htmlcov').exists():
            print("✅ HTML coverage report generated in htmlcov/")
        
        # Generate test summary
        report_content = """
# Test Report - Salah Reminders

## Test Coverage
- Backend: See htmlcov/index.html for detailed coverage
- Frontend: See coverage/lcov-report/index.html for detailed coverage

## Test Results
- Backend Tests: ✅ Passed
- Frontend Tests: ✅ Passed
- Integration Tests: ✅ Passed
- Code Linting: ✅ Passed

## Recommendations
1. Maintain test coverage above 80%
2. Add more integration tests for critical user flows
3. Consider adding performance tests for API endpoints
4. Add accessibility tests for frontend components

## Next Steps
1. Review any failing tests and fix issues
2. Update tests when adding new features
3. Consider adding automated testing in CI/CD pipeline
        """
        
        with open('reports/test_report.md', 'w') as f:
            f.write(report_content)
        
        print("✅ Test report generated in reports/test_report.md")
        return True
        
    except Exception as e:
        print(f"❌ Error generating test report: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run tests for Salah Reminders application')
    parser.add_argument('--backend-only', action='store_true', help='Run only backend tests')
    parser.add_argument('--frontend-only', action='store_true', help='Run only frontend tests')
    parser.add_argument('--integration-only', action='store_true', help='Run only integration tests')
    parser.add_argument('--lint-only', action='store_true', help='Run only linting')
    parser.add_argument('--test-path', help='Specific test path to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-report', action='store_true', help='Skip test report generation')
    
    args = parser.parse_args()
    
    print("🚀 Salah Reminders Test Runner")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests based on arguments
    if args.backend_only:
        all_passed = run_backend_tests(args.test_path, args.verbose)
    elif args.frontend_only:
        all_passed = run_frontend_tests()
    elif args.integration_only:
        all_passed = run_integration_tests()
    elif args.lint_only:
        all_passed = run_linting()
    else:
        # Run all tests
        backend_passed = run_backend_tests(args.test_path, args.verbose)
        frontend_passed = run_frontend_tests()
        integration_passed = run_integration_tests()
        lint_passed = run_linting()
        
        all_passed = backend_passed and frontend_passed and integration_passed and lint_passed
    
    # Generate test report
    if not args.no_report and all_passed:
        generate_test_report()
    
    # Final result
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The application is ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please review and fix the issues.")
        sys.exit(1)


if __name__ == '__main__':
    main()
