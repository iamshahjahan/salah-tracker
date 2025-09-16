#!/usr/bin/env python3
"""Ruff linting check script for CI/CD pipeline."""

import os
import subprocess
import sys


def run_ruff_check():
    """Run Ruff linting check and return exit code."""
    print("🔍 Running Ruff linting check...")

    try:
        # Run ruff check
        result = subprocess.run(
            ["ruff", "check", ".", "--output-format=concise"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        if result.stdout:
            print("Ruff found issues:")
            print(result.stdout)

        if result.stderr:
            print("Ruff errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ All Ruff checks passed!")
            return 0
        print(f"❌ Ruff found {result.returncode} issues")
        return result.returncode

    except FileNotFoundError:
        print("❌ Ruff not found. Please install it with: pip install ruff")
        return 1
    except Exception as e:
        print(f"❌ Error running Ruff: {e}")
        return 1


def run_ruff_format_check():
    """Run Ruff format check and return exit code."""
    print("🎨 Running Ruff format check...")

    try:
        # Run ruff format check
        result = subprocess.run(
            ["ruff", "format", "--check", "."],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        if result.stdout:
            print("Format issues found:")
            print(result.stdout)

        if result.returncode == 0:
            print("✅ All files are properly formatted!")
            return 0
        print("❌ Some files need formatting")
        return result.returncode

    except FileNotFoundError:
        print("❌ Ruff not found. Please install it with: pip install ruff")
        return 1
    except Exception as e:
        print(f"❌ Error running Ruff format check: {e}")
        return 1


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--format-only":
        return run_ruff_format_check()
    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        return run_ruff_check()
    # Run both checks
    lint_exit_code = run_ruff_check()
    format_exit_code = run_ruff_format_check()

    if lint_exit_code == 0 and format_exit_code == 0:
        print("\n🎉 All Ruff checks passed!")
        return 0
    print(f"\n💥 Ruff checks failed (lint: {lint_exit_code}, format: {format_exit_code})")
    return max(lint_exit_code, format_exit_code)


if __name__ == "__main__":
    sys.exit(main())
