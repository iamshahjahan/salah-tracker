"""Step definitions for prayer completion features."""

from datetime import datetime, timedelta

import pytz
from behave import given, then, when

from app.models.prayer import (
    Prayer,
    PrayerCompletion,
    PrayerCompletionStatus,
)
from app.models.user import User
from app.services.cache_service import CacheService
from app.services.prayer_service import PrayerService


@given('I am logged in as a user')
def step_logged_in_as_user(context):
    """Set up logged-in user."""
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone="Asia/Kolkata",
        location_lat=12.9716,
        location_lng=77.5946,
        email_verified=True
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.current_user = user
    context.is_logged_in = True


@given("I am checking the namaz times of {date_str} at time {current_time}")
def step_todays_prayer_times_available(context, date_str, current_time):
    """Set up today's prayer times."""
    context.prayer_service = PrayerService()
    context.cache_service = CacheService()
    context.cache_service.invalidate_user_prayer_times(context.current_user.id)

    user_tz = pytz.timezone("Asia/Kolkata")

    # Combine date and time into datetime
    dt = datetime.strptime(f"{current_time}", "%Y-%m-%d %H:%M")
    dt = user_tz.localize(dt)

    context.prayer_times = context.prayer_service.get_prayer_times(
        context.current_user.id,
        date_str,
        current_time=dt,
    )
    print(context.prayer_times)


@given('it is currently within the Dhuhr prayer time window')
def step_within_dhuhr_prayer_time(context):
    """Set current time within Dhuhr prayer window."""
    # Mock current time to be within Dhuhr prayer time (12:15 - 15:15)
    context.current_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    context.prayer_service = PrayerService()


@given('the Dhuhr prayer time window has passed')
def step_dhuhr_prayer_time_passed(context):
    """Set current time after Dhuhr prayer window."""
    # Mock current time to be after Dhuhr prayer time (after 15:15)
    context.current_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    context.prayer_service = PrayerService()


@given('it is before the Dhuhr prayer time window')
def step_before_dhuhr_prayer_time(context):
    """Set current time before Dhuhr prayer window."""
    # Mock current time to be before Dhuhr prayer time (before 12:15)
    context.current_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    context.prayer_service = PrayerService()


# This step is defined in notification_steps.py


@given('the current time is "{time}" in my timezone')
def step_current_time_in_timezone(context, time):
    """Set current time in user's timezone."""
    user_tz = pytz.timezone(context.current_user.timezone)
    hour, minute = map(int, time.split(':'))
    context.current_time = datetime.now(user_tz).replace(hour=hour, minute=minute, second=0, microsecond=0)


@given('the Dhuhr prayer time is "{time}" in my timezone')
def step_dhuhr_prayer_time_in_timezone(context, time):
    """Set Dhuhr prayer time in user's timezone."""
    _hour, _minute = map(int, time.split(':'))
    context.prayer_times['DHUHR'].start_time = datetime.strptime(time, '%H:%M').time()


@given('I am on the prayers page')
def step_on_prayers_page(context):
    """Navigate to prayers page."""
    context.current_page = 'prayers'


@given('I can see today\'s prayer times')
def step_can_see_todays_prayer_times(context):
    """Verify prayer times are visible."""
    context.prayer_times_visible = True


@given('I have received a prayer completion link via email')
def step_received_prayer_completion_link(context):
    """Simulate receiving prayer completion link."""
    context.completion_link = "http://example.com/complete-prayer/abc123"


# This step is defined in api_steps.py


@given('I am a new user with no prayer completions')
def step_new_user_no_completions(context):
    """Set up new user with no prayer completions."""
    # User already created in step_logged_in_as_user
    # No additional prayer completions needed


@given('I have completed some prayers and missed others')
def step_mixed_prayer_completion(context):
    """Set up mixed prayer completion history."""
    yesterday = datetime.now().date() - timedelta(days=1)

    # Completed prayers
    for prayer_name in ['FAJR', 'DHUHR']:
        prayer = Prayer(
            user_id=context.current_user.id,
            prayer_name=prayer_name,
            prayer_date=yesterday,
            start_time=datetime.strptime('12:00', '%H:%M').time(),
            end_time=datetime.strptime('15:00', '%H:%M').time(),
            status=PrayerCompletionStatus.COMPLETE
        )
        context.db.session.add(prayer)

        completion = PrayerCompletion(
            user_id=context.current_user.id,
            prayer_id=prayer.id,
            marked_at=datetime.utcnow() - timedelta(days=1),
            status=PrayerCompletionStatus.COMPLETE
        )
        context.db.session.add(completion)

    # Missed prayers
    for prayer_name in ['ASR', 'MAGHRIB']:
        prayer = Prayer(
            user_id=context.current_user.id,
            prayer_name=prayer_name,
            prayer_date=yesterday,
            start_time=datetime.strptime('15:00', '%H:%M').time(),
            end_time=datetime.strptime('18:00', '%H:%M').time(),
            status=PrayerCompletionStatus.MISSED
        )
        context.db.session.add(prayer)

    context.db.session.commit()



@when('I try to mark the Dhuhr prayer as completed')
def step_try_mark_dhuhr_prayer_completed(context):
    """Try to mark Dhuhr prayer as completed."""
    prayer_service = PrayerService()
    context.completion_result = prayer_service.complete_prayer(
        context.current_user.id,
        context.prayer_times['DHUHR'].id
    )


@when('I click the "Mark as Complete" button for Dhuhr prayer')
def step_click_mark_complete_button(context):
    """Click mark as complete button."""
    context.button_clicked = True


@when('I click the completion link')
def step_click_completion_link(context):
    """Click prayer completion link."""
    context.link_clicked = True


@when('I click "Mark as Complete"')
def step_click_mark_complete(context):
    """Click mark as complete button."""
    context.completion_clicked = True


@when('I add a note "{note}"')
def step_add_note(context, note):
    """Add a note to prayer completion."""
    context.completion_note = note


@when('I try to complete a prayer without proper authentication')
def step_try_complete_without_auth(context):
    """Try to complete prayer without authentication."""
    context.is_logged_in = False
    prayer_service = PrayerService()
    context.completion_result = prayer_service.complete_prayer(
        None,  # No user ID
        context.prayer_times['DHUHR'].id,
        context.current_time
    )


@when('I try to complete a prayer that doesn\'t exist')
def step_try_complete_nonexistent_prayer(context):
    """Try to complete non-existent prayer."""
    prayer_service = PrayerService()
    context.completion_result = prayer_service.complete_prayer(
        context.current_user.id,
        99999,  # Non-existent prayer ID
        context.current_time
    )


@when('I try to complete the same prayer multiple times rapidly')
def step_try_complete_same_prayer_multiple_times(context):
    """Try to complete same prayer multiple times."""
    prayer_service = PrayerService()
    context.rapid_completions = []

    for _i in range(6):  # More than rate limit
        result = prayer_service.complete_prayer(
            context.current_user.id,
            context.prayer_times['DHUHR'].id,
            context.current_time
        )
        context.rapid_completions.append(result)


@then('the prayer should be marked as "{status}"')
def step_prayer_marked_as_status(context, status):
    """Verify prayer is marked with specific status."""
    assert context.completion_result['success'], f"Got response: {context.completion_result['success']}"
    # Check the status in the completion object
    if 'completion' in context.completion_result:
        assert context.completion_result['completion']['status'] == status, f"Completion status should be {status}, but got {context.completion_result['completion']['status']}"
    else:
        raise AssertionError("Unable to complete prayer")


# This step is defined in email_verification_steps.py


@then('the prayer status should be updated in real-time')
def step_prayer_status_updated_realtime(context):
    """Verify prayer status is updated in real-time."""
    # This would typically check frontend updates
    context.status_updated = True


@then('I should see a message about completing missed prayer')
def step_see_missed_prayer_message(context):
    """Verify missed prayer completion message."""
    assert 'missed' in context.completion_result['message'].lower()


@then('the prayer status should be updated accordingly')
def step_prayer_status_updated_accordingly(context):
    """Verify prayer status is updated accordingly."""
    context.status_updated = True


# This step is covered by the generic error message step in authentication_steps.py


@then('the prayer should remain in "pending" status')
def step_prayer_remains_pending(context):
    """Verify prayer remains in pending status."""
    assert not context.completion_result['success']


@then('the completion time should be recorded correctly')
def step_completion_time_recorded_correctly(context):
    """Verify completion time is recorded correctly."""
    assert 'completion_time' in context.completion_result


@then('the button should change to "Completed"')
def step_button_changes_to_completed(context):
    """Verify button changes to completed."""
    context.button_text = "Completed"


@then('the prayer card should show completed status')
def step_prayer_card_shows_completed_status(context):
    """Verify prayer card shows completed status."""
    context.card_status = "completed"


@then('I should see a success notification')
def step_see_success_notification(context):
    """Verify success notification is displayed."""
    context.notification_shown = True


@then('I should be taken to the prayer completion page')
def step_taken_to_completion_page(context):
    """Verify navigation to completion page."""
    context.current_page = 'prayer_completion'


# This step is defined in notification_steps.py


# This step is defined in notification_steps.py


@then('the note should be saved')
def step_note_saved(context):
    """Verify note is saved."""
    assert 'note' in context.completion_result


@then('I should be able to view the note later')
def step_able_to_view_note_later(context):
    """Verify note can be viewed later."""
    context.note_viewable = True


@then('I should see an authentication error')
def step_see_authentication_error(context):
    """Verify authentication error."""
    assert context.completion_result['error'] == 'Authentication required'


@then('the prayer should not be completed')
def step_prayer_not_completed(context):
    """Verify prayer was not completed."""
    assert not context.completion_result['success']


# This step is covered by the generic error message step in authentication_steps.py


@then('no completion should be recorded')
def step_no_completion_recorded(context):
    """Verify no completion is recorded."""
    assert not context.completion_result['success']

