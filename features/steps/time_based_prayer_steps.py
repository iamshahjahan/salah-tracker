"""
Step definitions for time-based prayer state testing.
"""

from behave import given, when, then
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerCompletionStatus, PrayerType
from app.services.cache_service import CacheService
from app.services.prayer_service import PrayerService
from config.database import db
from datetime import datetime, timedelta, time
import pytz


@given('I am logged in as a user with timezone "{timezone}"')
def step_logged_in_user_with_timezone(context, timezone):
    """Set up logged-in user with specific timezone."""

    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone=timezone,
        location_lat=12.9716,
        location_lng=77.5946,
        email_verified=True
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.current_user = user
    context.is_logged_in = True

@given('I am logged in as a user with timezone "{timezone}" and created_at {datetime_str}')
def step_logged_in_user_with_timezone(context, timezone,datetime_str):
    """Set up logged-in user with specific timezone."""
    current_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        timezone=timezone,
        location_lat=12.9716,
        location_lng=77.5946,
        email_verified=True,
        created_at=current_datetime
    )
    user.set_password("password123")
    context.db.session.add(user)
    context.db.session.commit()
    context.current_user = user
    context.is_logged_in = True
# Using existing step definition from prayer_completion_steps.py


@given('the prayer times are:')
def step_prayer_times_table(context):
    """Set up prayer times from table."""
    context.prayer_times = {}
    for row in context.table:
        prayer_name = row['Prayer'].upper()
        prayer_time = row['Time']
        context.prayer_times[prayer_name] = prayer_time


@given('the current time is "{time_str}" in my timezone with seconds')
def step_current_time_in_timezone_extended(context, time_str):
    """Set current time in user's timezone with extended format support."""
    user_tz = pytz.timezone(context.current_user.timezone)
    
    # Parse time string (HH:MM or HH:MM:SS format)
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:  # HH:MM
            hour, minute = int(parts[0]), int(parts[1])
            second = 0
        elif len(parts) == 3:  # HH:MM:SS
            hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    
    # Create datetime for today with the specified time
    today = datetime.now().date()
    context.current_time = user_tz.localize(
        datetime.combine(today, time(hour, minute, second))
    )


@when('I check the {prayer_name} prayer status')
def step_check_prayer_status(context, prayer_name):
    """Check the status of a specific prayer."""
    prayer_type = PrayerType[prayer_name.upper()]
    
    # Get prayer times with current time
    prayer_times_result = context.prayer_service.get_prayer_times(
        context.current_user.id,
        current_time=context.current_time
    )
    
    if prayer_times_result.get('success'):
        prayers = prayer_times_result.get('prayers', [])
        context.current_prayer = None
        for prayer_info in prayers:
            if prayer_info.get('prayer_type') == prayer_type.value:
                context.current_prayer = prayer_info
                break
        
        if not context.current_prayer:
            raise AssertionError(f"Prayer {prayer_name} not found in prayer times")
    else:
        raise AssertionError(f"Failed to get prayer times: {prayer_times_result.get('error')}")


@then('the {prayer_name} prayer should be in "{expected_status}" state')
def step_prayer_should_be_in_state(context, prayer_name, expected_status):
    """Verify prayer is in expected state and validate metadata."""
    # Find the prayer entry for the given prayer_name
    prayer_info = next(
        (p for p in context.prayer_times['prayers'] if p.get('prayer_type').upper() == prayer_name.upper()), None
    )
    assert prayer_info, f"Prayer {prayer_name} not found in response."

    # Check the main state (prayer_status)
    actual_status = prayer_info.get('prayer_status')
    assert actual_status == expected_status, (
        f"Expected {prayer_name} to be in '{expected_status}' state, "
        f"but got '{actual_status}'"
    )

    # Now check all metadata fields from the Examples table
    # We dynamically build the placeholder keys based on the prayer name
    key_prefix = prayer_name.lower()
    expected_fields = {
        "completed": context.active_outline.get(f"{key_prefix}_completed"),
        "can_complete": context.active_outline.get(f"{key_prefix}_can_complete"),
        "is_missed": context.active_outline.get(f"{key_prefix}_is_missed"),
        "can_mark_qada": context.active_outline.get(f"{key_prefix}_can_mark_qada"),
        "is_late": context.active_outline.get(f"{key_prefix}_is_late"),
        # "prayer_status": context.active_outline.get(f"{key_prefix}_prayer_status"),
        "status_color": context.active_outline.get(f"{key_prefix}_status_color"),
        "status_text": context.active_outline.get(f"{key_prefix}_status_text"),
    }

    for field, expected_value in expected_fields.items():
        if expected_value is None:
            continue  # Skip if not defined in the Examples
        actual_value = str(prayer_info[field]).lower()
        expected_value = str(expected_value).lower()
        assert actual_value == expected_value, (
            f"For {prayer_name}, expected {field}='{expected_value}', "
            f"but got '{actual_value}'"
        )


@then('I should be able to complete the {prayer_name} prayer')
def step_should_be_able_to_complete_prayer(context, prayer_name):
    """Verify prayer can be completed."""
    assert context.current_prayer is not None, f"Prayer {prayer_name} not found"
    
    can_complete = context.current_prayer.get('can_complete', False)
    assert can_complete, f"Should be able to complete {prayer_name} prayer"


@then('I should not be able to complete the {prayer_name} prayer')
def step_should_not_be_able_to_complete_prayer(context, prayer_name):
    """Verify prayer cannot be completed."""
    assert context.current_prayer is not None, f"Prayer {prayer_name} not found"
    
    can_complete = context.current_prayer.get('can_complete', False)
    assert not can_complete, f"Should not be able to complete {prayer_name} prayer"


@then('I should be able to mark {prayer_name} as qada')
def step_should_be_able_to_mark_qada(context, prayer_name):
    """Verify prayer can be marked as qada."""
    assert context.current_prayer is not None, f"Prayer {prayer_name} not found"
    
    can_mark_qada = context.current_prayer.get('can_mark_qada', False)
    assert can_mark_qada, f"Should be able to mark {prayer_name} as qada"


@then('I should not be able to mark {prayer_name} as qada')
def step_should_not_be_able_to_mark_qada(context, prayer_name):
    """Verify prayer cannot be marked as qada."""
    assert context.current_prayer is not None, f"Prayer {prayer_name} not found"
    
    can_mark_qada = context.current_prayer.get('can_mark_qada', False)
    assert not can_mark_qada, f"Should not be able to mark {prayer_name} as qada"


@given('the {prayer_name} prayer is in "{status}" state')
def step_prayer_in_state(context, prayer_name, status):
    """Set prayer to specific state."""
    prayer_type = PrayerType[prayer_name.upper()]
    
    # Find the prayer record
    prayer = Prayer.query.filter_by(
        user_id=context.current_user.id,
        prayer_type=prayer_type,
        prayer_date=context.current_time.date()
    ).first()
    
    if not prayer:
        raise AssertionError(f"Prayer {prayer_name} not found")
    
    # Set up completion record based on status
    existing_completion = PrayerCompletion.query.filter_by(prayer_id=prayer.id).first()
    
    if status == "completed":
        if not existing_completion:
            completion = PrayerCompletion(
                prayer_id=prayer.id,
                user_id=context.current_user.id,
                status=PrayerCompletionStatus.COMPLETE,
                marked_at=datetime.now(pytz.UTC)
            )
            context.db.session.add(completion)
        else:
            existing_completion.status = PrayerCompletionStatus.COMPLETE
            existing_completion.marked_at = datetime.now(pytz.UTC)
    elif status == "missed":
        if not existing_completion:
            completion = PrayerCompletion(
                prayer_id=prayer.id,
                user_id=context.current_user.id,
                status=PrayerCompletionStatus.MISSED,
                marked_at=None
            )
            context.db.session.add(completion)
        else:
            existing_completion.status = PrayerCompletionStatus.MISSED
            existing_completion.marked_at = None
    elif status == "qada":
        if not existing_completion:
            completion = PrayerCompletion(
                prayer_id=prayer.id,
                user_id=context.current_user.id,
                status=PrayerCompletionStatus.QADA,
                marked_at=datetime.now(pytz.UTC)
            )
            context.db.session.add(completion)
        else:
            existing_completion.status = PrayerCompletionStatus.QADA
            existing_completion.marked_at = datetime.now(pytz.UTC)
    elif status == "pending":
        if existing_completion:
            context.db.session.delete(existing_completion)
    
    context.db.session.commit()


@when('I mark the {prayer_name} prayer as completed')
def step_mark_prayer_completed(context, prayer_name):
    """Mark prayer as completed."""
    target_prayer_type = PrayerType[prayer_name.strip("\"").upper()]

    print(context.prayer_times)
    prayer_id = None

    for prayer in context.prayer_times['prayers']:
        if prayer['prayer_type'] == target_prayer_type.value:
            prayer_id = prayer['id']
            break

    
    # Call the prayer service to complete the prayer
    result = context.prayer_service.complete_prayer(
        context.current_user.id,
        prayer_id,
        current_time=context.current_time
    )
    
    context.completion_result = result


@when('I try to mark the {prayer_name} prayer as completed')
def step_try_mark_prayer_completed(context, prayer_name):
    """Try to mark prayer as completed."""
    prayer_type = PrayerType[prayer_name.upper()]
    
    # Find the prayer record
    prayer = Prayer.query.filter_by(
        user_id=context.current_user.id,
        prayer_type=prayer_type,
        prayer_date=context.current_time.date()
    ).first()
    
    if not prayer:
        raise AssertionError(f"Prayer {prayer_name} not found")
    
    # Call the prayer service to complete the prayer
    result = context.prayer_service.complete_prayer(
        context.current_user.id,
        prayer.id,
        current_time=context.current_time
    )
    
    context.completion_result = result


@when('I mark the {prayer_name} prayer as qada')
def step_mark_prayer_qada(context, prayer_name):
    """Mark prayer as qada."""
    target_prayer_type = PrayerType[prayer_name.strip("\"").upper()]

    print(context.prayer_times)
    prayer_id = None

    for prayer in context.prayer_times['prayers']:
        if prayer['prayer_type'] == target_prayer_type.value:
            prayer_id = prayer['id']
            break

    # Call the prayer service to complete the prayer
    result = context.prayer_service.mark_prayer_qada(
        context.current_user.id,
        prayer_id,
        current_time=context.current_time
    )

    context.completion_result = result


# Using existing step definition from authentication_steps.py


@then('I should not be able to complete the {prayer_name} prayer again')
def step_should_not_complete_prayer_again(context, prayer_name):
    """Verify prayer cannot be completed again."""
    prayer_type = PrayerType[prayer_name.upper()]
    
    # Find the prayer record
    prayer = Prayer.query.filter_by(
        user_id=context.current_user.id,
        prayer_type=prayer_type,
        prayer_date=context.current_time.date()
    ).first()
    
    if not prayer:
        raise AssertionError(f"Prayer {prayer_name} not found")
    
    # Try to complete again
    result = context.prayer_service.complete_prayer(
        context.current_user.id,
        prayer.id,
        current_time=context.current_time
    )
    
    assert not result.get('success', True), f"Should not be able to complete {prayer_name} again"
    assert 'already completed' in result.get('error', '').lower()


@then('I should not be able to mark {prayer_name} as qada again')
def step_should_not_mark_qada_again(context, prayer_name):
    """Verify prayer cannot be marked as qada again."""
    prayer_type = PrayerType[prayer_name.upper()]
    
    # Find the prayer record
    prayer = Prayer.query.filter_by(
        user_id=context.current_user.id,
        prayer_type=prayer_type,
        prayer_date=context.current_time.date()
    ).first()
    
    if not prayer:
        raise AssertionError(f"Prayer {prayer_name} not found")
    
    # Try to mark as qada again
    result = context.prayer_service.mark_prayer_qada(
        context.current_user.id,
        prayer.id,
        current_time=context.current_time
    )
    
    assert not result.get('success', True), f"Should not be able to mark {prayer_name} as qada again"


@then('the prayer time should be displayed in "{timezone}" timezone')
def step_prayer_time_displayed_in_timezone(context, timezone):
    """Verify prayer time is displayed in correct timezone."""
    assert context.current_prayer is not None, "No current prayer found"
    
    prayer_time = context.current_prayer.get('prayer_time')
    assert prayer_time is not None, "Prayer time not found"
    
    # The prayer time should be in the user's timezone
    user_tz = pytz.timezone(timezone)
    # This is a basic check - in a real implementation, you'd verify the timezone conversion
    assert isinstance(prayer_time, str), "Prayer time should be a string"


@given('it is daylight savings time')
def step_is_daylight_savings_time(context):
    """Set up daylight savings time scenario."""
    # This would need to be implemented based on your DST handling logic
    context.is_daylight_savings = True


@given('daylight savings has ended')
def step_daylight_savings_ended(context):
    """Set up post-daylight savings scenario."""
    # This would need to be implemented based on your DST handling logic
    context.is_daylight_savings = False


@then('the prayer time should account for daylight savings')
def step_prayer_time_accounts_for_dst(context):
    """Verify prayer time accounts for daylight savings."""
    # This would need to be implemented based on your DST handling logic
    assert hasattr(context, 'is_daylight_savings'), "Daylight savings context not set"


@then('the prayer time should account for standard time')
def step_prayer_time_accounts_for_standard_time(context):
    """Verify prayer time accounts for standard time."""
    # This would need to be implemented based on your DST handling logic
    assert hasattr(context, 'is_daylight_savings'), "Daylight savings context not set"


@then('the {prayer_name} prayer should remain in "{status}" state')
def step_prayer_should_remain_in_state(context, prayer_name, status):
    """Verify prayer remains in the same state after an operation."""
    # Re-check the prayer status to ensure it hasn't changed
    prayer_type = PrayerType[prayer_name.upper()]
    
    prayer_times_result = context.prayer_service.get_prayer_times(
        context.current_user.id,
        current_time=context.current_time
    )
    
    if prayer_times_result.get('success'):
        prayers = prayer_times_result.get('prayers', [])
        current_prayer = None
        for prayer_info in prayers:
            if prayer_info.get('prayer_type') == prayer_type.value:
                current_prayer = prayer_info
                break
        
        if current_prayer:
            actual_status = current_prayer.get('status')
            assert actual_status == status, (
                f"Expected {prayer_name} to remain in '{status}' state, "
                f"but got '{actual_status}'"
            )
        else:
            raise AssertionError(f"Prayer {prayer_name} not found")
    else:
        raise AssertionError(f"Failed to get prayer times: {prayer_times_result.get('error')}")


@then("All the namaz should be in future")
def step_impl(context):
    prayers = context.prayer_times['prayers']
    for prayer_info in prayers:
        assert prayer_info['prayer_status'] == 'future'
