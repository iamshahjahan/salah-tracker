#!/usr/bin/env python3
"""
BDD Test Runner for Salah Tracker
Runs Behavior-Driven Development tests using Behave framework.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 5 minutes")
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking BDD Dependencies...")
    
    dependencies = [
        ('behave', 'behave --version'),
        ('flask', 'python3 -c "import flask; print(flask.__version__)"'),
        ('sqlalchemy', 'python3 -c "import sqlalchemy; print(sqlalchemy.__version__)"'),
        ('pytest', 'python3 -c "import pytest; print(pytest.__version__)"')
    ]
    
    missing_deps = []
    
    for dep_name, check_cmd in dependencies:
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {dep_name}: {result.stdout.strip()}")
        else:
            print(f"❌ {dep_name}: Not installed")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install them with: pip3 install behave flask sqlalchemy pytest")
        return False
    
    return True


def run_bdd_tests(tags=None, feature_path=None, format_type='pretty', output_dir='reports'):
    """Run BDD tests with specified parameters."""
    print("🚀 Salah Tracker - BDD Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Build behave command
    cmd_parts = ['behave']
    
    # Add format
    cmd_parts.extend(['--format', format_type])
    
    # Add output directory
    cmd_parts.extend(['--outdir', output_dir])
    
    # Add tags if specified
    if tags:
        if isinstance(tags, list):
            tags = ','.join(tags)
        cmd_parts.extend(['--tags', tags])
    
    # Add feature path
    if feature_path:
        cmd_parts.append(feature_path)
    else:
        cmd_parts.append('features')
    
    # Add additional options
    cmd_parts.extend([
        '--no-capture',
        '--no-capture-stderr',
        '--logging-level=INFO'
    ])
    
    command = ' '.join(cmd_parts)
    
    # Run the tests
    result = run_command(command, "BDD Tests")
    
    return result


def run_smoke_tests():
    """Run smoke tests (critical functionality)."""
    print("🔥 Running Smoke Tests...")
    return run_bdd_tests(tags='@smoke', format_type='pretty')


def run_regression_tests():
    """Run full regression test suite."""
    print("🔄 Running Regression Tests...")
    return run_bdd_tests(tags='@regression', format_type='html')


def run_api_tests():
    """Run API-specific tests."""
    print("🔌 Running API Tests...")
    return run_bdd_tests(tags='@api', format_type='json')


def run_ui_tests():
    """Run UI-specific tests."""
    print("🖥️ Running UI Tests...")
    return run_bdd_tests(tags='@ui', format_type='pretty')


def generate_report():
    """Generate HTML report from test results."""
    print("📊 Generating Test Report...")
    
    # Check if reports directory exists
    if not os.path.exists('reports'):
        print("❌ No reports directory found. Run tests first.")
        return False
    
    # Generate summary report
    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salah Tracker - BDD Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .test-result {{ margin: 10px 0; padding: 10px; border-radius: 3px; }}
            .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
            .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Salah Tracker - BDD Test Report</h1>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="summary">
            <h2>Test Summary</h2>
            <p>This report contains the results of BDD tests run using the Behave framework.</p>
        </div>
    </body>
    </html>
    """
    
    with open('reports/bdd_test_report.html', 'w') as f:
        f.write(report_content)
    
    print("✅ Report generated: reports/bdd_test_report.html")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run BDD tests for Salah Tracker')
    parser.add_argument('--tags', help='Tags to run (e.g., @smoke,@api)')
    parser.add_argument('--feature', help='Specific feature to run')
    parser.add_argument('--format', choices=['pretty', 'json', 'html'], default='pretty',
                       help='Output format')
    parser.add_argument('--output', default='reports', help='Output directory')
    parser.add_argument('--smoke', action='store_true', help='Run smoke tests only')
    parser.add_argument('--regression', action='store_true', help='Run regression tests')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--ui', action='store_true', help='Run UI tests only')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies only')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    if args.check_deps:
        print("✅ All dependencies are installed!")
        return
    
    # Run specific test suites
    if args.smoke:
        result = run_smoke_tests()
    elif args.regression:
        result = run_regression_tests()
    elif args.api:
        result = run_api_tests()
    elif args.ui:
        result = run_ui_tests()
    else:
        # Run all tests or specific tags/features
        result = run_bdd_tests(
            tags=args.tags,
            feature_path=args.feature,
            format_type=args.format,
            output_dir=args.output
        )
    
    # Generate report if requested
    if args.report:
        generate_report()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 BDD TEST SUMMARY")
    print("="*60)
    
    if result['success']:
        print("✅ All BDD tests passed!")
        print("🎉 Ready for deployment.")
    else:
        print("❌ Some BDD tests failed!")
        print("🔧 Please fix the issues before deployment.")
        if result['stderr']:
            print(f"Error details: {result['stderr']}")
    
    print(f"📁 Reports saved to: {args.output}")
    print("="*60)
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
