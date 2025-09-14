"""
Comprehensive Database Operations Tests
Tests all database operations, relationships, and data integrity.
"""

import pytest
from datetime import datetime, timedelta, date
from config.database import db
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification
from app.models.inspirational_content import QuranicVerse, Hadith
from app.models.family_group import FamilyGroup
from app.models.family import FamilyMember
from app.models.email_verification import EmailVerification


class TestUserModel:
    """Test User model operations"""
    
    def test_create_user(self, app):
        """Test creating a new user"""
        with app.app_context():
            user = User(
                username='testuser_db',
                email='testuser_db@example.com',
                password_hash='hashed_password',
                location='Test City',
                latitude=40.7128,
                longitude=-74.0060,
                timezone='America/New_York'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser_db'
            assert user.email == 'testuser_db@example.com'
            assert user.created_at is not None
    
    def test_user_password_hashing(self, app):
        """Test password hashing functionality"""
        with app.app_context():
            user = User(
                username='testuser_hash',
                email='testuser_hash@example.com',
                password_hash='plain_password',
                location='Test City'
            )
            
            # Test setting password
            user.set_password('new_password')
            assert user.password_hash != 'new_password'
            assert user.check_password('new_password')
            assert not user.check_password('wrong_password')
    
    def test_user_relationships(self, app, test_user):
        """Test user relationships with other models"""
        with app.app_context():
            # Test prayer completions relationship
            completion = PrayerCompletion(
                user_id=test_user.id,
                prayer_id=1,
                completed_at=datetime.now(),
                is_qada=False
            )
            db.session.add(completion)
            db.session.commit()
            
            assert len(test_user.prayer_completions) >= 1
            assert completion in test_user.prayer_completions
            
            # Test notifications relationship
            notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=1,
                notification_type='reminder',
                message='Test notification',
                scheduled_time=datetime.now() + timedelta(minutes=5)
            )
            db.session.add(notification)
            db.session.commit()
            
            assert len(test_user.notifications) >= 1
            assert notification in test_user.notifications
    
    def test_user_soft_delete(self, app):
        """Test user soft delete functionality"""
        with app.app_context():
            user = User(
                username='testuser_delete',
                email='testuser_delete@example.com',
                password_hash='hashed_password',
                location='Test City'
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Soft delete user
            user.is_deleted = True
            db.session.commit()
            
            # Verify user is marked as deleted
            deleted_user = User.query.get(user_id)
            assert deleted_user.is_deleted is True
            
            # Test that deleted users are filtered out
            active_users = User.query.filter_by(is_deleted=False).all()
            assert user not in active_users


class TestPrayerModel:
    """Test Prayer model operations"""
    
    def test_prayer_creation(self, app):
        """Test creating prayer records"""
        with app.app_context():
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=1
            )
            db.session.add(prayer)
            db.session.commit()
            
            assert prayer.id is not None
            assert prayer.name == 'FAJR'
            assert prayer.display_name == 'Fajr'
            assert prayer.prayer_time == '05:30:00'
    
    def test_prayer_completion_creation(self, app, test_user):
        """Test creating prayer completion records"""
        with app.app_context():
            completion = PrayerCompletion(
                user_id=test_user.id,
                prayer_id=1,
                completed_at=datetime.now(),
                is_qada=False,
                completion_method='manual'
            )
            db.session.add(completion)
            db.session.commit()
            
            assert completion.id is not None
            assert completion.user_id == test_user.id
            assert completion.prayer_id == 1
            assert completion.is_qada is False
            assert completion.completion_method == 'manual'
    
    def test_prayer_completion_relationships(self, app, test_user):
        """Test prayer completion relationships"""
        with app.app_context():
            # Create a prayer
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=test_user.id
            )
            db.session.add(prayer)
            db.session.commit()
            
            # Create completion
            completion = PrayerCompletion(
                user_id=test_user.id,
                prayer_id=prayer.id,
                completed_at=datetime.now(),
                is_qada=False
            )
            db.session.add(completion)
            db.session.commit()
            
            # Test relationships
            assert completion.user == test_user
            assert completion.prayer == prayer
            assert completion in test_user.prayer_completions
            assert completion in prayer.completions
    
    def test_prayer_status_enum(self, app):
        """Test prayer status enum values"""
        with app.app_context():
            prayer = Prayer(
                name='FAJR',
                display_name='Fajr',
                prayer_time='05:30:00',
                date=date.today(),
                user_id=1,
                status='pending'
            )
            db.session.add(prayer)
            db.session.commit()
            
            # Test valid status values
            valid_statuses = ['pending', 'completed', 'missed', 'qada']
            for status in valid_statuses:
                prayer.status = status
                db.session.commit()
                assert prayer.status == status


class TestNotificationModel:
    """Test PrayerNotification model operations"""
    
    def test_notification_creation(self, app, test_user):
        """Test creating notification records"""
        with app.app_context():
            notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=1,
                notification_type='reminder',
                message='Test reminder notification',
                scheduled_time=datetime.now() + timedelta(minutes=15),
                is_sent=False
            )
            db.session.add(notification)
            db.session.commit()
            
            assert notification.id is not None
            assert notification.user_id == test_user.id
            assert notification.notification_type == 'reminder'
            assert notification.is_sent is False
    
    def test_notification_types(self, app, test_user):
        """Test different notification types"""
        with app.app_context():
            notification_types = ['reminder', 'window_reminder', 'qada_reminder']
            
            for notif_type in notification_types:
                notification = PrayerNotification(
                    user_id=test_user.id,
                    prayer_id=1,
                    notification_type=notif_type,
                    message=f'Test {notif_type}',
                    scheduled_time=datetime.now() + timedelta(minutes=5)
                )
                db.session.add(notification)
            
            db.session.commit()
            
            # Verify all notifications were created
            notifications = PrayerNotification.query.filter_by(user_id=test_user.id).all()
            assert len(notifications) >= len(notification_types)
    
    def test_notification_scheduling(self, app, test_user):
        """Test notification scheduling functionality"""
        with app.app_context():
            # Create past notification
            past_notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=1,
                notification_type='reminder',
                message='Past notification',
                scheduled_time=datetime.now() - timedelta(hours=1),
                is_sent=True
            )
            
            # Create future notification
            future_notification = PrayerNotification(
                user_id=test_user.id,
                prayer_id=2,
                notification_type='reminder',
                message='Future notification',
                scheduled_time=datetime.now() + timedelta(hours=1),
                is_sent=False
            )
            
            db.session.add_all([past_notification, future_notification])
            db.session.commit()
            
            # Test querying unsent notifications
            unsent_notifications = PrayerNotification.query.filter_by(
                user_id=test_user.id,
                is_sent=False
            ).all()
            
            assert future_notification in unsent_notifications
            assert past_notification not in unsent_notifications


class TestFamilyModels:
    """Test Family and FamilyGroup model operations"""
    
    def test_family_group_creation(self, app, test_user):
        """Test creating family groups"""
        with app.app_context():
            family_group = FamilyGroup(
                name='Test Family',
                description='Test family group',
                created_by=test_user.id,
                group_code='TEST123'
            )
            db.session.add(family_group)
            db.session.commit()
            
            assert family_group.id is not None
            assert family_group.name == 'Test Family'
            assert family_group.group_code == 'TEST123'
            assert family_group.created_by == test_user.id
    
    def test_family_membership(self, app, test_user):
        """Test family membership relationships"""
        with app.app_context():
            # Create family group
            family_group = FamilyGroup(
                name='Test Family',
                description='Test family group',
                created_by=test_user.id,
                group_code='TEST123'
            )
            db.session.add(family_group)
            db.session.commit()
            
            # Create family membership
            family = FamilyMember(
                user_id=test_user.id,
                family_group_id=family_group.id,
                role='admin',
                joined_at=datetime.now()
            )
            db.session.add(family)
            db.session.commit()
            
            # Test relationships
            assert family.user == test_user
            assert family.family_group == family_group
            assert family in test_user.family_memberships
            assert family in family_group.members
    
    def test_family_group_roles(self, app, test_user):
        """Test family group role management"""
        with app.app_context():
            family_group = FamilyGroup(
                name='Test Family',
                description='Test family group',
                created_by=test_user.id,
                group_code='TEST123'
            )
            db.session.add(family_group)
            db.session.commit()
            
            # Test different roles
            roles = ['admin', 'member', 'viewer']
            for role in roles:
                family = FamilyMember(
                    user_id=test_user.id,
                    family_group_id=family_group.id,
                    role=role,
                    joined_at=datetime.now()
                )
                db.session.add(family)
            
            db.session.commit()
            
            # Verify roles were set correctly
            families = Family.query.filter_by(family_group_id=family_group.id).all()
            assert len(families) == len(roles)


class TestInspirationalContentModel:
    """Test InspirationalContent model operations"""
    
    def test_quranic_verse_creation(self, app):
        """Test creating Quranic verse"""
        with app.app_context():
            verse = QuranicVerse(
                surah_number=1,
                surah_name_arabic='الفاتحة',
                surah_name_english='Al-Fatiha',
                verse_number=1,
                arabic_text='بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
                english_translation='In the name of Allah, the Entirely Merciful, the Especially Merciful.',
                category='guidance',
                is_active=True
            )
            db.session.add(verse)
            db.session.commit()
            
            assert verse.id is not None
            assert verse.surah_name_english == 'Al-Fatiha'
            assert verse.category == 'guidance'
            assert verse.is_active is True
    
    def test_hadith_creation(self, app):
        """Test creating Hadith"""
        with app.app_context():
            hadith = Hadith(
                collection='Bukhari',
                hadith_number='1',
                arabic_text='إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ',
                english_translation='Actions are according to intentions.',
                narrator='Umar ibn al-Khattab',
                category='guidance',
                is_active=True
            )
            db.session.add(hadith)
            db.session.commit()
            
            assert hadith.id is not None
            assert hadith.collection == 'Bukhari'
            assert hadith.category == 'guidance'
            assert hadith.is_active is True
    
    def test_content_types(self, app):
        """Test different content types"""
        with app.app_context():
            # Create verses with different categories
            categories = ['prayer', 'patience', 'guidance', 'forgiveness']
            
            for category in categories:
                verse = QuranicVerse(
                    surah_number=1,
                    surah_name_arabic='الفاتحة',
                    surah_name_english='Al-Fatiha',
                    verse_number=1,
                    arabic_text='Test verse',
                    english_translation='Test translation',
                    category=category,
                    is_active=True
                )
                db.session.add(verse)
            
            db.session.commit()
            
            # Verify all categories were created
            verses = QuranicVerse.query.filter_by(is_active=True).all()
            assert len(verses) >= len(categories)


class TestEmailVerificationModel:
    """Test EmailVerification model operations"""
    
    def test_email_verification_creation(self, app, test_user):
        """Test creating email verification records"""
        with app.app_context():
            verification = EmailVerification(
                user_id=test_user.id,
                email=test_user.email,
                verification_code='123456',
                expires_at=datetime.now() + timedelta(hours=24),
                is_verified=False
            )
            db.session.add(verification)
            db.session.commit()
            
            assert verification.id is not None
            assert verification.user_id == test_user.id
            assert verification.verification_code == '123456'
            assert verification.is_verified is False
    
    def test_verification_expiry(self, app, test_user):
        """Test email verification expiry"""
        with app.app_context():
            # Create expired verification
            expired_verification = EmailVerification(
                user_id=test_user.id,
                email=test_user.email,
                verification_code='123456',
                expires_at=datetime.now() - timedelta(hours=1),
                is_verified=False
            )
            
            # Create valid verification
            valid_verification = EmailVerification(
                user_id=test_user.id,
                email=test_user.email,
                verification_code='654321',
                expires_at=datetime.now() + timedelta(hours=1),
                is_verified=False
            )
            
            db.session.add_all([expired_verification, valid_verification])
            db.session.commit()
            
            # Test querying valid verifications
            valid_verifications = EmailVerification.query.filter(
                EmailVerification.expires_at > datetime.now()
            ).all()
            
            assert valid_verification in valid_verifications
            assert expired_verification not in valid_verifications


class TestDatabaseConstraints:
    """Test database constraints and validations"""
    
    def test_unique_email_constraint(self, app):
        """Test unique email constraint"""
        with app.app_context():
            # Create first user
            user1 = User(
                username='user1',
                email='test@example.com',
                password_hash='hashed_password',
                location='Test City'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try to create second user with same email
            user2 = User(
                username='user2',
                email='test@example.com',  # Same email
                password_hash='hashed_password',
                location='Test City'
            )
            db.session.add(user2)
            
            # Should raise integrity error
            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()
    
    def test_foreign_key_constraints(self, app):
        """Test foreign key constraints"""
        with app.app_context():
            # Try to create prayer completion with non-existent user
            completion = PrayerCompletion(
                user_id=99999,  # Non-existent user
                prayer_id=1,
                completed_at=datetime.now(),
                is_qada=False
            )
            db.session.add(completion)
            
            # Should raise integrity error
            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()
    
    def test_not_null_constraints(self, app):
        """Test NOT NULL constraints"""
        with app.app_context():
            # Try to create user without required fields
            user = User()  # Missing required fields
            db.session.add(user)
            
            # Should raise integrity error
            with pytest.raises(Exception):  # IntegrityError or similar
                db.session.commit()


class TestDatabaseTransactions:
    """Test database transaction handling"""
    
    def test_transaction_rollback(self, app):
        """Test transaction rollback on error"""
        with app.app_context():
            # Start transaction
            db.session.begin()
            
            try:
                # Create user
                user = User(
                    username='testuser_tx',
                    email='testuser_tx@example.com',
                    password_hash='hashed_password',
                    location='Test City'
                )
                db.session.add(user)
                db.session.flush()  # Flush to get user ID
                
                # Try to create invalid prayer completion
                completion = PrayerCompletion(
                    user_id=user.id,
                    prayer_id=99999,  # Invalid prayer ID
                    completed_at=datetime.now(),
                    is_qada=False
                )
                db.session.add(completion)
                db.session.commit()
                
            except Exception:
                # Rollback on error
                db.session.rollback()
            
            # Verify user was not created due to rollback
            user_check = User.query.filter_by(username='testuser_tx').first()
            assert user_check is None
    
    def test_bulk_operations(self, app, test_user):
        """Test bulk database operations"""
        with app.app_context():
            # Create multiple prayer completions
            completions = []
            for i in range(5):
                completion = PrayerCompletion(
                    user_id=test_user.id,
                    prayer_id=i + 1,
                    completed_at=datetime.now(),
                    is_qada=False
                )
                completions.append(completion)
            
            # Bulk insert
            db.session.add_all(completions)
            db.session.commit()
            
            # Verify all were created
            user_completions = PrayerCompletion.query.filter_by(user_id=test_user.id).all()
            assert len(user_completions) >= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
