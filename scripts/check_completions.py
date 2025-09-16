#!/usr/bin/env python3
"""Script to check current prayer completion entries in the database."""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date

from app.models.prayer import Prayer, PrayerCompletion
from app.models.user import User
from main import app


def check_completions():
    """Check current prayer completion entries."""
    with app.app_context():
        try:
            # Check for any completion entries
            completions = PrayerCompletion.query.all()
            print(f"Found {len(completions)} prayer completion entries:")

            for completion in completions:
                print(f"\n--- Completion ID: {completion.id} ---")
                print(f"User ID: {completion.user_id}")
                print(f"Prayer ID: {completion.prayer_id}")
                print(f"Completed At: {completion.completed_at}")
                print(f"Is Qada: {completion.is_qada}")
                print(f"Is Late: {completion.is_late}")
                print(f"Notes: {completion.notes}")

                # Get prayer details
                prayer = Prayer.query.get(completion.prayer_id)
                if prayer:
                    print(f"Prayer: {prayer.prayer_type.value} at {prayer.prayer_time} on {prayer.prayer_date}")

            # Check today's prayers specifically
            today = date.today()
            print(f"\n--- Today's Prayers ({today}) ---")

            user = User.query.first()
            if user:
                today_prayers = Prayer.query.filter_by(
                    user_id=user.id,
                    prayer_date=today
                ).all()

                for prayer in today_prayers:
                    completion = PrayerCompletion.query.filter_by(
                        prayer_id=prayer.id,
                        user_id=user.id
                    ).first()

                    status = "Has completion" if completion else "No completion"
                    print(f"{prayer.prayer_type.value} ({prayer.prayer_time}): {status}")

        except Exception as e:
            print(f"❌ Error checking completions: {e!s}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_completions()
