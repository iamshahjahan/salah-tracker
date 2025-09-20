"""Step definitions for notification features."""

from datetime import datetime

from behave import then

from app.tasks.prayer_reminders import _process_user_reminders
from app.utils import timezone_utils


@then('I am sending a reminder for the user at "{datetime_str}"')
def step_receive_prayer_reminder_email(context, datetime_str):
    current_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

    # Convert to user's timezone
    sent_count, failed_count = _process_user_reminders(context.current_user, timezone_utils.to_utc(current_datetime,context.current_user.timezone))
    context.sent_count = sent_count
    context.failed_count = failed_count

@then('There should be "{count}" notification')
def step_check_one_notification(context,count):
    assert str(context.sent_count) == str(count), f"Expected {count}, got {context.sent_count}"
    assert context.failed_count == 0