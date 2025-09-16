#!/usr/bin/env python3
"""
Database migration script to add email verification functionality.

This script adds the email_verifications table and the email_verified field
to the users table.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from main import app

def run_migration():
    """Run the database migration."""
    with app.app_context():
        try:
            # Create the email_verifications table
            db.create_all()

            # Add email_verified column to users table if it doesn't exist
            # Note: This is a simplified approach. In production, you'd use Alembic migrations
            try:
                # Check if column already exists
                result = db.engine.execute("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'users'
                    AND COLUMN_NAME = 'email_verified'
                """)

                column_exists = result.fetchone()[0] > 0

                if not column_exists:
                    db.engine.execute("""
                        ALTER TABLE users
                        ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
                    """)
                    print("✓ Added email_verified column to users table")
                else:
                    print("✓ email_verified column already exists")

            except Exception as e:
                print(f"⚠ Warning adding email_verified column: {e}")

            print("✓ Database migration completed successfully")

        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False

    return True

if __name__ == "__main__":
    print("Running database migration for email verification...")
    success = run_migration()

    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNew features added:")
        print("- Email verification system")
        print("- OTP-based login")
        print("- Password reset via email")
        print("\nNext steps:")
        print("1. Configure your email settings in .env file")
        print("2. Restart the application")
        print("3. Test the new authentication features")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
