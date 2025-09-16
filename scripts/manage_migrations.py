#!/usr/bin/env python3
"""Flask-Migrate Management Script
Provides easy commands for managing database migrations.
"""

import os
import subprocess
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def show_help():
    """Show help information."""
    print("""
🗄️  Flask-Migrate Management Script

Usage: python3 scripts/manage_migrations.py <command>

Commands:
  init          - Initialize Flask-Migrate (if not already done)
  status        - Show current migration status
  history       - Show migration history
  create <msg>  - Create a new migration with message
  upgrade       - Apply all pending migrations
  downgrade     - Rollback one migration
  current       - Show current database revision
  heads         - Show all migration heads
  help          - Show this help message

Examples:
  python3 scripts/manage_migrations.py create "Add user preferences table"
  python3 scripts/manage_migrations.py upgrade
  python3 scripts/manage_migrations.py status
""")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    # Set environment variables
    os.environ['FLASK_APP'] = 'main.py'

    if command == 'help':
        show_help()
    elif command == 'init':
        run_command('flask db init', 'Initializing Flask-Migrate')
    elif command == 'status':
        run_command('flask db current', 'Checking current migration status')
    elif command == 'history':
        run_command('flask db history', 'Showing migration history')
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Please provide a migration message")
            print("Usage: python3 scripts/manage_migrations.py create \"Your message here\"")
            return
        message = sys.argv[2]
        run_command(f'flask db migrate -m "{message}"', f'Creating migration: {message}')
    elif command == 'upgrade':
        run_command('flask db upgrade', 'Applying pending migrations')
    elif command == 'downgrade':
        run_command('flask db downgrade', 'Rolling back one migration')
    elif command == 'current':
        run_command('flask db current', 'Showing current database revision')
    elif command == 'heads':
        run_command('flask db heads', 'Showing migration heads')
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
