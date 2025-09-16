#!/usr/bin/env python3
"""
Migration to add composite index on prayers table for user_id, prayer_type, prayer_date
This will improve query performance for prayer lookups by user and date.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config.database import db
from sqlalchemy import text

def add_prayer_index():
    """Add composite index on prayers table"""
    
    with app.app_context():
        try:
            # Check if index already exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'prayers' 
                AND index_name = 'idx_prayers_user_type_date'
            """))
            
            index_exists = result.fetchone()[0] > 0
            
            if index_exists:
                print("✅ Index 'idx_prayers_user_type_date' already exists")
                return True
            
            # Create the composite index
            print("🔧 Creating composite index on prayers table...")
            db.session.execute(text("""
                CREATE INDEX idx_prayers_user_type_date 
                ON prayers (user_id, prayer_type, prayer_date)
            """))
            
            db.session.commit()
            print("✅ Successfully created index 'idx_prayers_user_type_date' on prayers table")
            
            # Verify the index was created
            result = db.session.execute(text("""
                SELECT index_name, column_name, seq_in_index
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'prayers' 
                AND index_name = 'idx_prayers_user_type_date'
                ORDER BY seq_in_index
            """))
            
            index_columns = result.fetchall()
            print("📊 Index details:")
            for row in index_columns:
                print(f"   - {row[1]} (position {row[2]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            db.session.rollback()
            return False

def remove_prayer_index():
    """Remove the composite index from prayers table"""
    
    with app.app_context():
        try:
            # Check if index exists
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'prayers' 
                AND index_name = 'idx_prayers_user_type_date'
            """))
            
            index_exists = result.fetchone()[0] > 0
            
            if not index_exists:
                print("ℹ️  Index 'idx_prayers_user_type_date' does not exist")
                return True
            
            # Drop the index
            print("🗑️  Dropping index 'idx_prayers_user_type_date' from prayers table...")
            db.session.execute(text("""
                DROP INDEX idx_prayers_user_type_date ON prayers
            """))
            
            db.session.commit()
            print("✅ Successfully dropped index 'idx_prayers_user_type_date' from prayers table")
            return True
            
        except Exception as e:
            print(f"❌ Error dropping index: {e}")
            db.session.rollback()
            return False

def show_prayer_indexes():
    """Show all indexes on the prayers table"""
    
    with app.app_context():
        try:
            result = db.session.execute(text("""
                SELECT 
                    index_name,
                    column_name,
                    seq_in_index,
                    non_unique,
                    index_type
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'prayers'
                ORDER BY index_name, seq_in_index
            """))
            
            indexes = result.fetchall()
            
            if not indexes:
                print("📊 No indexes found on prayers table")
                return
            
            print("📊 Indexes on prayers table:")
            current_index = None
            for row in indexes:
                index_name, column_name, seq_in_index, non_unique, index_type = row
                
                if index_name != current_index:
                    current_index = index_name
                    unique_text = "UNIQUE" if non_unique == 0 else "NON-UNIQUE"
                    print(f"\n🔍 {index_name} ({unique_text}, {index_type})")
                
                print(f"   - {column_name} (position {seq_in_index})")
            
        except Exception as e:
            print(f"❌ Error showing indexes: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage prayer table indexes")
    parser.add_argument("action", choices=["add", "remove", "show"], 
                       help="Action to perform: add, remove, or show indexes")
    
    args = parser.parse_args()
    
    if args.action == "add":
        success = add_prayer_index()
        sys.exit(0 if success else 1)
    elif args.action == "remove":
        success = remove_prayer_index()
        sys.exit(0 if success else 1)
    elif args.action == "show":
        show_prayer_indexes()
        sys.exit(0)
