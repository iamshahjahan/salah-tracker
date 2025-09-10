#!/usr/bin/env python3
"""
Database setup script for SalahReminders
This script creates the MySQL database and initializes the tables
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='khankhan'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            database_name = 'salah_reminders'
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            print(f"Database '{database_name}' created successfully or already exists")
            
            # Use the database
            cursor.execute(f"USE {database_name}")
            
            # Show tables to verify
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Current tables in {database_name}: {tables}")
            
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

def create_tables():
    """Create tables using Flask-SQLAlchemy"""
    try:
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("All tables created successfully!")
            
            # Show created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {tables}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    print("Setting up SalahReminders database...")
    print("=" * 50)
    
    # Step 1: Create database
    print("Step 1: Creating MySQL database...")
    create_database()
    
    print("\n" + "=" * 50)
    
    # Step 2: Create tables
    print("Step 2: Creating database tables...")
    create_tables()
    
    print("\n" + "=" * 50)
    print("Database setup completed!")
    print("You can now run the application with: python3 app.py")
