#!/usr/bin/env python3
"""Prayer State Matrix Validation Script.

This script runs comprehensive prayer state matrix tests and provides
detailed validation results across different dates, times, and timezones.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_behave_test(feature_file, tags=None, format_type="json"):
    """Run behave test and return results."""
    cmd = ["python3", "-m", "behave", feature_file]

    if tags:
        cmd.extend(["--tags", tags])

    if format_type == "json":
        cmd.extend(["--format", "json", "--outfile", "test_results.json"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def parse_test_results():
    """Parse test results from JSON file."""
    try:
        with open("test_results.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def generate_matrix_summary():
    """Generate a comprehensive summary of the prayer state matrix."""
    print("=" * 80)
    print("PRAYER STATE MATRIX VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test coverage summary
    print("TEST COVERAGE:")
    print("-" * 40)
    print("• 100+ test conditions across different dates and times")
    print("• 4 major timezones (Asia/Kolkata, America/New_York, Europe/London, Asia/Dubai)")
    print("• 4 seasonal dates (Summer Solstice, Winter Solstice, Spring Equinox, Fall Equinox)")
    print("• Edge cases (Midnight transitions, Leap Year, Year End/Start)")
    print("• All 5 prayer types (Fajr, Dhuhr, Asr, Maghrib, Isha)")
    print("• All prayer states (future, pending, missed, completed, qada)")
    print()

    # Prayer time windows
    print("PRAYER TIME WINDOWS:")
    print("-" * 40)
    print("• Fajr: 05:21 - 12:15 (ends at Dhuhr)")
    print("• Dhuhr: 12:15 - 15:45 (ends at Asr)")
    print("• Asr: 15:45 - 18:30 (ends at Maghrib)")
    print("• Maghrib: 18:30 - 19:45 (ends at Isha)")
    print("• Isha: 19:45 - 05:21 (ends at next day's Fajr)")
    print()

    # Test scenarios
    print("TEST SCENARIOS:")
    print("-" * 40)
    print("1. Summer Solstice (June 21, 2025) - Longest day")
    print("2. Winter Solstice (December 21, 2025) - Shortest day")
    print("3. Spring Equinox (March 20, 2025) - Equal day/night")
    print("4. Fall Equinox (September 22, 2025) - Equal day/night")
    print("5. Leap Year (February 29, 2024)")
    print("6. Year End/Start (December 31, 2024 - January 1, 2025)")
    print("7. Midnight Transitions")
    print("8. Multiple Timezones")
    print()

    # Expected behaviors
    print("EXPECTED BEHAVIORS:")
    print("-" * 40)
    print("• Future: Before prayer time - Cannot complete, cannot mark as qada")
    print("• Pending: During prayer window - Can complete, cannot mark as qada")
    print("• Missed: After prayer window - Cannot complete, can mark as qada")
    print("• Completed: Prayer completed in time - Terminal state")
    print("• Qada: Prayer completed late - Terminal state")
    print()


def run_matrix_validation():
    """Run the complete prayer state matrix validation."""
    print("Starting Prayer State Matrix Validation...")
    print()

    # Check if feature file exists
    feature_file = "features/prayer_tracking/prayer_state_matrix.feature"
    if not os.path.exists(feature_file):
        print(f"ERROR: Feature file not found: {feature_file}")
        return False

    # Generate summary
    generate_matrix_summary()

    # Run the tests
    print("RUNNING TESTS:")
    print("-" * 40)

    # Run dry-run first to check step definitions
    print("1. Checking step definitions...")
    returncode, stdout, stderr = run_behave_test(feature_file, format_type="text")

    if returncode != 0:
        print("❌ Step definition check failed!")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False
    print("✅ Step definitions are valid")

    # Run actual tests
    print("2. Running prayer state matrix tests...")
    returncode, stdout, stderr = run_behave_test(feature_file, format_type="json")

    if returncode == 0:
        print("✅ All tests passed!")

        # Parse and display results
        results = parse_test_results()
        if results:
            print("\nDETAILED RESULTS:")
            print("-" * 40)

            for feature in results:
                if feature.get('name') == 'Prayer State Matrix - Comprehensive Date and Time Validation':
                    for scenario in feature.get('elements', []):
                        if scenario.get('type') == 'scenario':
                            name = scenario.get('name', 'Unknown')
                            status = scenario.get('status', 'unknown')
                            duration = scenario.get('duration', 0)

                            status_icon = "✅" if status == "passed" else "❌"
                            print(f"{status_icon} {name} ({duration}ms)")

        return True
    print("❌ Some tests failed!")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    # Try to parse partial results
    results = parse_test_results()
    if results:
        print("\nPARTIAL RESULTS:")
        print("-" * 40)
        for feature in results:
            for scenario in feature.get('elements', []):
                if scenario.get('type') == 'scenario':
                    name = scenario.get('name', 'Unknown')
                    status = scenario.get('status', 'unknown')
                    status_icon = "✅" if status == "passed" else "❌"
                    print(f"{status_icon} {name}")

    return False


def main():
    """Main function."""
    print("Prayer State Matrix Validation Tool")
    print("=" * 50)

    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run validation
    success = run_matrix_validation()

    # Clean up
    if os.path.exists("test_results.json"):
        os.remove("test_results.json")

    print("\n" + "=" * 80)
    if success:
        print("🎉 PRAYER STATE MATRIX VALIDATION COMPLETED SUCCESSFULLY!")
        print("All 100+ test conditions have been validated.")
    else:
        print("❌ PRAYER STATE MATRIX VALIDATION FAILED!")
        print("Please check the test results and fix any issues.")
    print("=" * 80)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
