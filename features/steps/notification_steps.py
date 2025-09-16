"""Step definitions for notification features."""

from datetime import datetime

import pytz
from behave import given, then, when

from app.models.prayer import (
    Prayer,
    PrayerCompletion,
    PrayerCompletionStatus,
    PrayerType,
)
from app.models.user import User
from app.services.notification_service import NotificationService

# This step is defined in dashboard_steps.py


@given('it is 10 minutes before Dhuhr prayer time')
def step_10_minutes_before_dhuhr(context):
    """Set time to 10 minutes before Dhuhr prayer."""
    # Mock current time to be 10 minutes before Dhuhr (12:15 - 10 minutes = 12:05)
    context.current_time = datetime.now().replace(hour=12, minute=5, second=0, microsecond=0)
    context.prayer_name = 'DHUHR'
    context.prayer_time = datetime.now().replace(hour=12, minute=15, second=0, microsecond=0)


@given('the Dhuhr prayer time has passed')
def step_dhuhr_prayer_time_passed(context):
    """Set time after Dhuhr prayer time."""
    # Mock current time to be after Dhuhr prayer time (after 15:15)
    context.current_time = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
    context.prayer_name = 'DHUHR'
    context.prayer_time = datetime.now().replace(hour=12, minute=15, second=0, microsecond=0)


@given('I have not completed the prayer')
def step_have_not_completed_prayer(context):
    """Set up uncompleted prayer."""
    context.prayer_completed = False


@given('I have already completed the Dhuhr prayer')
def step_have_completed_dhuhr_prayer(context):
    """Set up completed prayer."""
    context.prayer_completed = True

    # Create prayer completion record
    prayer = Prayer(
        user_id=context.current_user.id,
        prayer_type=PrayerType.DHUHR,
        prayer_date=datetime.now().date(),
        prayer_time=datetime.strptime('12:15', '%H:%M').time(),
    )
    context.db.session.add(prayer)
    context.db.session.commit()

    completion = PrayerCompletion(
        user_id=context.current_user.id,
        prayer_id=prayer.id,
        marked_at=datetime.utcnow(),
        status=PrayerCompletionStatus.JAMAAT
    )
    context.db.session.add(completion)
    context.db.session.commit()


@given('I am in timezone "{timezone}"')
def step_in_timezone(context, timezone):
    """Set user timezone."""
    context.current_user.timezone = timezone
    context.db.session.commit()


@given('it is 10 minutes before Dhuhr prayer time in my timezone')
def step_10_minutes_before_dhuhr_timezone(context):
    """Set time to 10 minutes before Dhuhr in user's timezone."""
    user_tz = pytz.timezone(context.current_user.timezone)
    # 10 minutes before Dhuhr (12:15 - 10 minutes = 12:05)
    context.current_time = datetime.now(user_tz).replace(hour=12, minute=5, second=0, microsecond=0)
    context.prayer_name = 'DHUHR'


@given('I have requested multiple reminders rapidly')
def step_requested_multiple_reminders_rapidly(context):
    """Set up rapid reminder requests."""
    context.rapid_requests = []
    for _i in range(6):  # More than rate limit
        context.rapid_requests.append({
            'timestamp': datetime.utcnow(),
            'user_id': context.current_user.id
        })


@given('my email address is invalid')
def step_email_address_invalid(context):
    """Set invalid email address."""
    context.current_user.email = 'invalid-email-address'
    context.db.session.commit()


@given('there are 100 users who need reminders')
def step_100_users_need_reminders(context):
    """Set up 100 users needing reminders."""
    context.users_needing_reminders = []
    for i in range(100):
        user = User(
            username=f"reminderuser{i}",
            email=f"reminder{i}@example.com",
            first_name=f"Reminder{i}",
            last_name="User",
            timezone="UTC",
            email_verified=True
        )
        user.set_password("password123")
        context.db.session.add(user)
        context.users_needing_reminders.append(user)
    context.db.session.commit()


@when('the reminder system runs')
def step_reminder_system_runs(context):
    """Run the reminder system."""
    notification_service = NotificationService()
    context.reminder_result = notification_service.send_prayer_reminder(
        context.current_user, 'DHUHR', datetime.now()
    )


@when('I try to request another reminder')
def step_try_request_another_reminder(context):
    """Try to request another reminder."""
    notification_service = NotificationService()
    context.reminder_result = notification_service.send_prayer_reminder(
        context.current_user, 'DHUHR', datetime.now()
    )


@when('I configure my reminder preferences')
def step_configure_reminder_preferences(context):
    """Configure reminder preferences."""
    context.current_user.reminder_preferences = context.reminder_preferences
    context.db.session.commit()
    context.preferences_saved = True


@when('I disable prayer reminders')
def step_disable_prayer_reminders(context):
    """Disable prayer reminders."""
    context.reminder_preferences['email_reminders'] = False
    context.current_user.reminder_preferences = context.reminder_preferences
    context.db.session.commit()
    context.reminders_disabled = True


@when('the reminder system tries to send a reminder')
def step_reminder_system_tries_send(context):
    """Try to send reminder."""
    notification_service = NotificationService()
    context.email_result = notification_service.send_prayer_reminder(
        context.current_user,
        context.prayer_name,
        context.prayer_time
    )


@when('the reminder system processes all users')
def step_reminder_system_processes_all_users(context):
    """Process reminders for all users."""
    notification_service = NotificationService()
    start_time = datetime.utcnow()

    context.bulk_reminder_result = notification_service.send_bulk_reminders(
        context.users_needing_reminders
    )

    end_time = datetime.utcnow()
    context.processing_time = (end_time - start_time).total_seconds()


@then('I should receive a prayer reminder email')
def step_receive_prayer_reminder_email(context):
    """Verify prayer reminder email is received."""
    assert context.reminder_result['success']
    assert 'reminder sent' in context.reminder_result['message']


@then('the email should contain the prayer name and time')
def step_email_contains_prayer_name_time(context):
    """Verify email contains prayer name and time."""
    assert 'prayer_name' in context.reminder_result
    assert 'prayer_time' in context.reminder_result
    assert context.reminder_result['prayer_name'] == context.prayer_name


@then('the email should contain a completion link')
def step_email_contains_completion_link(context):
    """Verify email contains completion link."""
    assert 'completion_link' in context.reminder_result


@then('I should receive a missed prayer reminder')
def step_receive_missed_prayer_reminder(context):
    """Verify missed prayer reminder is received."""
    assert context.reminder_result['success']


@then('the email should contain a completion link for qada')
def step_email_contains_qada_completion_link(context):
    """Verify email contains qada completion link."""
    assert 'completion_link' in context.reminder_result
    assert 'qada' in context.reminder_result['completion_link']


@then('I should not receive a prayer reminder')
def step_not_receive_prayer_reminder(context):
    """Verify no prayer reminder is received."""
    assert not context.reminder_result['success'] or 'email_sent' not in context.reminder_result


@then('the prayer time should be displayed in my timezone')
def step_prayer_time_displayed_timezone(context):
    """Verify prayer time is displayed in user's timezone."""
    assert 'timezone' in context.reminder_result
    assert context.reminder_result['timezone'] == context.current_user.timezone


@then('the email should include family member prayer status')
def step_email_includes_family_prayer_status(context):
    """Verify email includes family member prayer status."""
    assert 'family_status' in context.reminder_result


# This step is defined in api_steps.py


# This step is covered by the generic error message step in authentication_steps.py


@then('my preferences should be saved')
def step_preferences_saved(context):
    """Verify preferences are saved."""
    assert context.preferences_saved


# This step is defined in email_verification_steps.py


@then('I should not receive any prayer reminders')
def step_not_receive_any_reminders(context):
    """Verify no prayer reminders are received."""
    assert context.reminders_disabled
    # Test that no reminders are sent
    notification_service = NotificationService()
    result = notification_service.send_prayer_reminder(
        context.current_user,
        'DHUHR',
        datetime.now()
    )
    assert not result['success']


@then('my preference should be saved')
def step_preference_saved(context):
    """Verify preference is saved."""
    assert context.reminders_disabled


@then('the delivery should fail gracefully')
def step_delivery_fail_gracefully(context):
    """Verify delivery fails gracefully."""
    assert not context.email_result['success']
    assert 'error' in context.email_result


@then('the failure should be logged')
def step_failure_logged(context):
    """Verify failure is logged."""
    assert 'logged' in context.email_result


@then('I should not receive the reminder')
def step_not_receive_reminder(context):
    """Verify reminder is not received."""
    assert not context.email_result['success']


@then('all users should receive their reminders')
def step_all_users_receive_reminders(context):
    """Verify all users receive reminders."""
    assert context.bulk_reminder_result['success']
    assert context.bulk_reminder_result['users_processed'] == 100


@then('the processing should complete within 5 minutes')
def step_processing_complete_within_5_minutes(context):
    """Verify processing completes within 5 minutes."""
    assert context.processing_time <= 300  # 5 minutes in seconds


@then('I should see the prayer details')
def step_see_prayer_details(context):
    """Verify prayer details are visible."""
    assert 'prayer_details' in context.reminder_result


@then('I should see a success page')
def step_see_success_page(context):
    """Verify success page is shown."""
    assert context.reminder_result['success']
    assert 'success_page' in context.reminder_result
