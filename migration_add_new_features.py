#!/usr/bin/env python3
"""
Database migration script to add new features.

This script adds the new models and fields for:
- Family groups
- Inspirational content (Quranic verses and Hadith)
- Prayer notifications
- Enhanced user profile fields
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
            # Create all new tables
            db.create_all()
            
            # Add new columns to users table if they don't exist
            new_columns = [
                ('city', 'VARCHAR(100)'),
                ('country', 'VARCHAR(100)'),
                ('fiqh_method', 'VARCHAR(20) DEFAULT "shafi"'),
                ('language', 'VARCHAR(10) DEFAULT "ar"'),
                ('email_notifications', 'BOOLEAN DEFAULT TRUE'),
                ('reminder_times', 'JSON')
            ]
            
            for column_name, column_def in new_columns:
                try:
                    # Check if column already exists
                    result = db.engine.execute(f"""
                        SELECT COUNT(*) as count 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME = 'users' 
                        AND COLUMN_NAME = '{column_name}'
                    """)
                    
                    column_exists = result.fetchone()[0] > 0
                    
                    if not column_exists:
                        db.engine.execute(f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_def}
                        """)
                        print(f"✓ Added {column_name} column to users table")
                    else:
                        print(f"✓ {column_name} column already exists")
                        
                except Exception as e:
                    print(f"⚠ Warning adding {column_name} column: {e}")
            
            # Insert sample Quranic verses
            insert_sample_verses()
            
            # Insert sample Hadith
            insert_sample_hadith()
            
            print("✓ Database migration completed successfully")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False
    
    return True

def insert_sample_verses():
    """Insert sample Quranic verses."""
    try:
        from app.models.inspirational_content import QuranicVerse
        
        # Check if verses already exist
        if QuranicVerse.query.first():
            print("✓ Sample Quranic verses already exist")
            return
        
        sample_verses = [
            {
                'surah_number': 2,
                'surah_name_arabic': 'البقرة',
                'surah_name_english': 'Al-Baqarah',
                'verse_number': 3,
                'arabic_text': 'الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ',
                'english_translation': 'Who believe in the unseen, establish prayer, and spend out of what We have provided for them.',
                'category': 'prayer'
            },
            {
                'surah_number': 29,
                'surah_name_arabic': 'العنكبوت',
                'surah_name_english': 'Al-Ankabut',
                'verse_number': 45,
                'arabic_text': 'وَأَقِمِ الصَّلَاةَ إِنَّ الصَّلَاةَ تَنْهَىٰ عَنِ الْفَحْشَاءِ وَالْمُنكَرِ',
                'english_translation': 'And establish prayer. Indeed, prayer prohibits immorality and wrongdoing.',
                'category': 'prayer'
            },
            {
                'surah_number': 2,
                'surah_name_arabic': 'البقرة',
                'surah_name_english': 'Al-Baqarah',
                'verse_number': 153,
                'arabic_text': 'يَا أَيُّهَا الَّذِينَ آمَنُوا اسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ إِنَّ اللَّهَ مَعَ الصَّابِرِينَ',
                'english_translation': 'O you who have believed, seek help through patience and prayer. Indeed, Allah is with the patient.',
                'category': 'patience'
            }
        ]
        
        for verse_data in sample_verses:
            verse = QuranicVerse(**verse_data)
            db.session.add(verse)
        
        db.session.commit()
        print("✓ Inserted sample Quranic verses")
        
    except Exception as e:
        print(f"⚠ Warning inserting Quranic verses: {e}")

def insert_sample_hadith():
    """Insert sample Hadith."""
    try:
        from app.models.inspirational_content import Hadith
        
        # Check if Hadith already exist
        if Hadith.query.first():
            print("✓ Sample Hadith already exist")
            return
        
        sample_hadith = [
            {
                'collection': 'Sahih Bukhari',
                'hadith_number': '8',
                'arabic_text': 'بُنِيَ الإِسْلاَمُ عَلَى خَمْسٍ: شَهَادَةِ أَنْ لاَ إِلَهَ إِلاَّ اللَّهُ وَأَنَّ مُحَمَّدًا رَسُولُ اللَّهِ، وَإِقَامِ الصَّلاَةِ، وَإِيتَاءِ الزَّكَاةِ، وَالْحَجِّ، وَصَوْمِ رَمَضَانَ',
                'english_translation': 'Islam is built upon five pillars: testifying that there is no god but Allah and that Muhammad is the Messenger of Allah, establishing prayer, giving zakah, performing Hajj, and fasting Ramadan.',
                'narrator': 'Abu Abdur-Rahman Abdullah ibn Umar ibn al-Khattab',
                'category': 'prayer'
            },
            {
                'collection': 'Sahih Muslim',
                'hadith_number': '151',
                'arabic_text': 'إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى',
                'english_translation': 'Actions are according to intentions, and every person will have what they intended.',
                'narrator': 'Umar ibn al-Khattab',
                'category': 'motivation'
            }
        ]
        
        for hadith_data in sample_hadith:
            hadith = Hadith(**hadith_data)
            db.session.add(hadith)
        
        db.session.commit()
        print("✓ Inserted sample Hadith")
        
    except Exception as e:
        print(f"⚠ Warning inserting Hadith: {e}")

if __name__ == "__main__":
    print("Running database migration for new features...")
    success = run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNew features added:")
        print("- Family groups functionality")
        print("- Inspirational content (Quranic verses and Hadith)")
        print("- Prayer notifications and reminders")
        print("- Enhanced user profile with fiqh selection")
        print("- Arabic language support")
        print("- Email notification preferences")
        print("\nNext steps:")
        print("1. Restart the application")
        print("2. Test the new features")
        print("3. Configure notification settings")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
