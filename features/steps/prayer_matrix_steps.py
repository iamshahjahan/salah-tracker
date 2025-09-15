"""
Step definitions for prayer state matrix testing.
"""

from behave import given, when, then
from app.models.user import User
from app.models.prayer import Prayer, PrayerCompletion, PrayerStatus, PrayerType
from app.services.cache_service import CacheService
from app.services.prayer_service import PrayerService
from config.database import db
from datetime import datetime, timedelta, time
import pytz


# Using existing step definition from time_based_prayer_steps.py

@given('I am checking the prayer times of {date} at time {datetime_str}')
def step_checking_prayer_times_at_datetime_matrix(context, date, datetime_str):
    """Set up prayer times check for specific date and datetime."""
    # Parse the date and datetime
    date = date.strip('"')
    datetime_str = datetime_str.strip('"')
    target_date = datetime.strptime(date, '%Y-%m-%d').date()
    current_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
    
    # Convert to user's timezone
    user_tz = pytz.timezone(context.current_user.timezone)
    context.current_time = user_tz.localize(current_datetime)
    
    # Initialize prayer service
    context.prayer_service = PrayerService()
    context.cache_service = CacheService()
    context.cache_service.invalidate_user_prayer_times(context.current_user.id)
    
    # Get prayer times for the specific date
    prayer_times_result = context.prayer_service.get_prayer_times(
        context.current_user.id,
        date_str=date,
        current_time=context.current_time
    )
    
    if prayer_times_result.get('success'):
        context.prayer_times = prayer_times_result
        context.prayers = prayer_times_result.get('prayers', [])
    else:
        raise AssertionError(f"Failed to get prayer times: {prayer_times_result.get('error')}")


# Using existing step definitions from time_based_prayer_steps.py


def _verify_prayer_state(context, prayer_type, expected_state):
    """Helper function to verify prayer state."""
    prayer_found = False
    
    for prayer_info in context.prayers:
        if prayer_info.get('prayer_type') == prayer_type:
            actual_state = prayer_info.get('status')
            assert actual_state == expected_state, (
                f"Expected {prayer_type} to be in '{expected_state}' state, "
                f"but got '{actual_state}' at {context.current_time}"
            )
            prayer_found = True
            break
    
    if not prayer_found:
        raise AssertionError(f"Prayer {prayer_type} not found in prayer times")


# Using existing step definitions from time_based_prayer_steps.py


@then('the prayer states should be:')
def step_prayer_states_should_be_table(context):
    """Verify prayer states from table."""
    for row in context.table:
        prayer_type = row['Prayer'].upper()
        expected_state = row['State']
        _verify_prayer_state(context, prayer_type, expected_state)


@then('I should see the following prayer times:')
def step_should_see_prayer_times_table(context):
    """Verify prayer times from table."""
    for row in context.table:
        prayer_type = row['Prayer'].upper()
        expected_time = row['Time']
        
        prayer_found = False
        for prayer_info in context.prayers:
            if prayer_info.get('prayer_type') == prayer_type:
                actual_time = prayer_info.get('prayer_time')
                assert actual_time == expected_time, (
                    f"Expected {prayer_type} time to be '{expected_time}', "
                    f"but got '{actual_time}'"
                )
                prayer_found = True
                break
        
        if not prayer_found:
            raise AssertionError(f"Prayer {prayer_type} not found in prayer times")


@then('the prayer completion rates should be:')
def step_prayer_completion_rates_should_be_table(context):
    """Verify prayer completion rates from table."""
    for row in context.table:
        prayer_type = row['Prayer'].upper()
        expected_rate = float(row['Rate'])
        
        prayer_found = False
        for prayer_info in context.prayers:
            if prayer_info.get('prayer_type') == prayer_type:
                actual_rate = prayer_info.get('completion_rate', 0)
                assert abs(actual_rate - expected_rate) < 0.01, (
                    f"Expected {prayer_type} completion rate to be {expected_rate}, "
                    f"but got {actual_rate}"
                )
                prayer_found = True
                break
        
        if not prayer_found:
            raise AssertionError(f"Prayer {prayer_type} not found in prayer times")


@then('the timezone should be "{expected_timezone}"')
def step_timezone_should_be(context, expected_timezone):
    """Verify the timezone is correct."""
    user_tz = pytz.timezone(context.current_user.timezone)
    assert str(user_tz) == expected_timezone, (
        f"Expected timezone to be '{expected_timezone}', "
        f"but got '{user_tz}'"
    )


@then('the current time should be "{expected_time}"')
def step_current_time_should_be(context, expected_time):
    """Verify the current time is correct."""
    expected_datetime = datetime.strptime(expected_time, '%Y-%m-%d %H:%M')
    user_tz = pytz.timezone(context.current_user.timezone)
    expected_datetime = user_tz.localize(expected_datetime)
    
    assert context.current_time == expected_datetime, (
        f"Expected current time to be '{expected_datetime}', "
        f"but got '{context.current_time}'"
    )


@then('the prayer window should be "{start_time}" to "{end_time}" for {prayer_type}')
def step_prayer_window_should_be(context, start_time, end_time, prayer_type):
    """Verify prayer window times."""
    prayer_type = prayer_type.upper()
    
    prayer_found = False
    for prayer_info in context.prayers:
        if prayer_info.get('prayer_type') == prayer_type:
            actual_start = prayer_info.get('window_start')
            actual_end = prayer_info.get('window_end')
            
            assert actual_start == start_time, (
                f"Expected {prayer_type} window start to be '{start_time}', "
                f"but got '{actual_start}'"
            )
            
            assert actual_end == end_time, (
                f"Expected {prayer_type} window end to be '{end_time}', "
                f"but got '{actual_end}'"
            )
            
            prayer_found = True
            break
    
    if not prayer_found:
        raise AssertionError(f"Prayer {prayer_type} not found in prayer times")


@then('the prayer should be "{action}" for {prayer_type}')
def step_prayer_should_be_action_for_type(context, action, prayer_type):
    """Verify prayer action availability."""
    prayer_type = prayer_type.upper()
    
    prayer_found = False
    for prayer_info in context.prayers:
        if prayer_info.get('prayer_type') == prayer_type:
            if action == "completable":
                can_complete = prayer_info.get('can_complete', False)
                assert can_complete, f"{prayer_type} should be completable but isn't"
            elif action == "not completable":
                can_complete = prayer_info.get('can_complete', False)
                assert not can_complete, f"{prayer_type} should not be completable but is"
            elif action == "qada markable":
                can_mark_qada = prayer_info.get('can_mark_qada', False)
                assert can_mark_qada, f"{prayer_type} should be qada markable but isn't"
            elif action == "not qada markable":
                can_mark_qada = prayer_info.get('can_mark_qada', False)
                assert not can_mark_qada, f"{prayer_type} should not be qada markable but is"
            
            prayer_found = True
            break
    
    if not prayer_found:
        raise AssertionError(f"Prayer {prayer_type} not found in prayer times")
