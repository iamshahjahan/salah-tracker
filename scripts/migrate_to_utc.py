#!/usr/bin/env python3
"""Migration script to convert existing datetime fields to UTC storage.

This script helps migrate existing data to use UTC storage format
and ensures all datetime fields are properly timezone-aware.
"""

import os
import sys

from zoneinfo import ZoneInfo

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.email_verification import EmailVerification
from app.models.family import FamilyMember
from app.models.family_group import FamilyGroup, FamilyGroupMember
from app.models.inspirational_content import Hadith, QuranicVerse
from app.models.prayer import Prayer, PrayerCompletion
from app.models.prayer_notification import PrayerNotification
from app.models.user import User
from config.database import db
from main import app


def migrate_user_datetimes():
    """Migrate User model datetime fields to UTC."""
    print("🔄 Migrating User model datetime fields...")

    users = User.query.all()
    updated_count = 0

    for user in users:
        needs_update = False

        # Update created_at if it's naive
        if user.created_at and user.created_at.tzinfo is None:
            user.created_at = user.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        # Update updated_at if it's naive
        if user.updated_at and user.updated_at.tzinfo is None:
            user.updated_at = user.updated_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} User records")


def migrate_prayer_datetimes():
    """Migrate Prayer model datetime fields to UTC."""
    print("🔄 Migrating Prayer model datetime fields...")

    prayers = Prayer.query.all()
    updated_count = 0

    for prayer in prayers:
        needs_update = False

        # Update created_at if it's naive
        if prayer.created_at and prayer.created_at.tzinfo is None:
            prayer.created_at = prayer.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} Prayer records")


def migrate_prayer_completion_datetimes():
    """Migrate PrayerCompletion model datetime fields to UTC."""
    print("🔄 Migrating PrayerCompletion model datetime fields...")

    completions = PrayerCompletion.query.all()
    updated_count = 0

    for completion in completions:
        needs_update = False

        # Update marked_at if it's naive
        if completion.marked_at and completion.marked_at.tzinfo is None:
            completion.marked_at = completion.marked_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} PrayerCompletion records")


def migrate_family_member_datetimes():
    """Migrate FamilyMember model datetime fields to UTC."""
    print("🔄 Migrating FamilyMember model datetime fields...")

    members = FamilyMember.query.all()
    updated_count = 0

    for member in members:
        needs_update = False

        # Update created_at if it's naive
        if member.created_at and member.created_at.tzinfo is None:
            member.created_at = member.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        # Update updated_at if it's naive
        if member.updated_at and member.updated_at.tzinfo is None:
            member.updated_at = member.updated_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} FamilyMember records")


def migrate_family_group_datetimes():
    """Migrate FamilyGroup model datetime fields to UTC."""
    print("🔄 Migrating FamilyGroup model datetime fields...")

    groups = FamilyGroup.query.all()
    updated_count = 0

    for group in groups:
        needs_update = False

        # Update created_at if it's naive
        if group.created_at and group.created_at.tzinfo is None:
            group.created_at = group.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        # Update updated_at if it's naive
        if group.updated_at and group.updated_at.tzinfo is None:
            group.updated_at = group.updated_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} FamilyGroup records")


def migrate_family_group_member_datetimes():
    """Migrate FamilyGroupMember model datetime fields to UTC."""
    print("🔄 Migrating FamilyGroupMember model datetime fields...")

    members = FamilyGroupMember.query.all()
    updated_count = 0

    for member in members:
        needs_update = False

        # Update joined_at if it's naive
        if member.joined_at and member.joined_at.tzinfo is None:
            member.joined_at = member.joined_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} FamilyGroupMember records")


def migrate_email_verification_datetimes():
    """Migrate EmailVerification model datetime fields to UTC."""
    print("🔄 Migrating EmailVerification model datetime fields...")

    verifications = EmailVerification.query.all()
    updated_count = 0

    for verification in verifications:
        needs_update = False

        # Update expires_at if it's naive
        if verification.expires_at and verification.expires_at.tzinfo is None:
            verification.expires_at = verification.expires_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        # Update created_at if it's naive
        if verification.created_at and verification.created_at.tzinfo is None:
            verification.created_at = verification.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} EmailVerification records")


def migrate_prayer_notification_datetimes():
    """Migrate PrayerNotification model datetime fields to UTC."""
    print("🔄 Migrating PrayerNotification model datetime fields...")

    notifications = PrayerNotification.query.all()
    updated_count = 0

    for notification in notifications:
        needs_update = False

        # Update sent_at if it's naive
        if notification.sent_at and notification.sent_at.tzinfo is None:
            notification.sent_at = notification.sent_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        # Update created_at if it's naive
        if notification.created_at and notification.created_at.tzinfo is None:
            notification.created_at = notification.created_at.replace(tzinfo=ZoneInfo('UTC'))
            needs_update = True

        if needs_update:
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} PrayerNotification records")


def migrate_inspirational_content_datetimes():
    """Migrate inspirational content model datetime fields to UTC."""
    print("🔄 Migrating inspirational content model datetime fields...")

    # Migrate QuranicVerse
    verses = QuranicVerse.query.all()
    updated_count = 0

    for verse in verses:
        if verse.created_at and verse.created_at.tzinfo is None:
            verse.created_at = verse.created_at.replace(tzinfo=ZoneInfo('UTC'))
            updated_count += 1

    # Migrate Hadith
    hadiths = Hadith.query.all()

    for hadith in hadiths:
        if hadith.created_at and hadith.created_at.tzinfo is None:
            hadith.created_at = hadith.created_at.replace(tzinfo=ZoneInfo('UTC'))
            updated_count += 1

    db.session.commit()
    print(f"✅ Updated {updated_count} inspirational content records")


def main():
    """Run the complete UTC migration."""
    print("🚀 Starting UTC migration for all models...")
    print("=" * 50)

    with app.app_context():
        try:
            # Run all migrations
            migrate_user_datetimes()
            migrate_prayer_datetimes()
            migrate_prayer_completion_datetimes()
            migrate_family_member_datetimes()
            migrate_family_group_datetimes()
            migrate_family_group_member_datetimes()
            migrate_email_verification_datetimes()
            migrate_prayer_notification_datetimes()
            migrate_inspirational_content_datetimes()

            print("=" * 50)
            print("🎉 UTC migration completed successfully!")
            print("✅ All datetime fields are now stored in UTC format")
            print("✅ All models have timezone-aware datetime handling")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    main()
