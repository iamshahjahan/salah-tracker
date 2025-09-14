#!/usr/bin/env python3
"""
Database migration script to update prayer completion status system.

This script updates the prayer_completions table to use the new status-based system:
- Renames completed_at to marked_at
- Replaces is_late and is_qada boolean fields with a single status enum field
- Updates existing records to use the new status system
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
            print("Starting prayer completion status migration...")
            
            # First, let's check if the new columns exist
            try:
                # Check if marked_at column exists
                result = db.engine.execute("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'prayer_completions'
                    AND COLUMN_NAME = 'marked_at'
                """)
                marked_at_exists = result.fetchone()[0] > 0
                
                # Check if status column exists
                result = db.engine.execute("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'prayer_completions'
                    AND COLUMN_NAME = 'status'
                """)
                status_exists = result.fetchone()[0] > 0
                
                if marked_at_exists and status_exists:
                    print("✓ New columns already exist, updating existing records...")
                else:
                    print("Adding new columns...")
                    
                    # Add marked_at column if it doesn't exist
                    if not marked_at_exists:
                        db.engine.execute("""
                            ALTER TABLE prayer_completions
                            ADD COLUMN marked_at DATETIME NULL
                        """)
                        print("✓ Added marked_at column")
                    
                    # Add status column if it doesn't exist
                    if not status_exists:
                        db.engine.execute("""
                            ALTER TABLE prayer_completions
                            ADD COLUMN status ENUM('PENDING', 'MISSED', 'COMPLETE', 'QADA') NOT NULL DEFAULT 'COMPLETE'
                        """)
                        print("✓ Added status column")
                
                # Update existing records to use new status system
                print("Updating existing records...")
                
                # Copy completed_at to marked_at for completed prayers
                db.engine.execute("""
                    UPDATE prayer_completions 
                    SET marked_at = completed_at 
                    WHERE completed_at IS NOT NULL
                """)
                print("✓ Copied completed_at to marked_at")
                
                # Update status based on old is_late and is_qada fields
                db.engine.execute("""
                    UPDATE prayer_completions 
                    SET status = CASE 
                        WHEN is_qada = 1 THEN 'QADA'
                        WHEN is_late = 1 THEN 'MISSED'
                        ELSE 'COMPLETE'
                    END
                """)
                print("✓ Updated status based on old fields")
                
                # For records that were marked as missed (is_late=1, is_qada=0), 
                # set marked_at to NULL since they weren't actually completed
                db.engine.execute("""
                    UPDATE prayer_completions 
                    SET marked_at = NULL 
                    WHERE is_late = 1 AND is_qada = 0
                """)
                print("✓ Set marked_at to NULL for missed prayers")
                
                # Drop old columns after successful migration
                print("Dropping old columns...")
                
                # Drop completed_at column
                try:
                    db.engine.execute("""
                        ALTER TABLE prayer_completions
                        DROP COLUMN completed_at
                    """)
                    print("✓ Dropped completed_at column")
                except Exception as e:
                    print(f"⚠ Warning dropping completed_at column: {e}")
                
                # Drop is_late column
                try:
                    db.engine.execute("""
                        ALTER TABLE prayer_completions
                        DROP COLUMN is_late
                    """)
                    print("✓ Dropped is_late column")
                except Exception as e:
                    print(f"⚠ Warning dropping is_late column: {e}")
                
                # Drop is_qada column
                try:
                    db.engine.execute("""
                        ALTER TABLE prayer_completions
                        DROP COLUMN is_qada
                    """)
                    print("✓ Dropped is_qada column")
                except Exception as e:
                    print(f"⚠ Warning dropping is_qada column: {e}")
                
                print("✓ Database migration completed successfully")
                
            except Exception as e:
                print(f"✗ Migration failed: {e}")
                return False
                
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False

    return True

if __name__ == "__main__":
    print("Running database migration for prayer completion status system...")
    success = run_migration()

    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nChanges made:")
        print("- Renamed completed_at to marked_at")
        print("- Replaced is_late and is_qada with status enum")
        print("- Updated existing records to use new status system")
        print("- Status values: pending, missed, complete, qada")
        print("\nNext steps:")
        print("1. Restart the application")
        print("2. Test the new prayer completion system")
        print("3. Verify that prayer status transitions work correctly")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
