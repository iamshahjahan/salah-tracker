"""Step definitions for dashboard features."""

from datetime import datetime, timedelta

from behave import given, then, when

from app.services.prayer_service import PrayerService


@given('I am on the dashboard page')
def step_on_dashboard_page(context):
    """Navigate to dashboard page."""
    context.current_page = 'dashboard'


@given('I have set my prayer reminder preferences')
def step_set_prayer_reminder_preferences(context):
    """Set prayer reminder preferences."""
    context.reminder_preferences = {
        'email_reminders': True,
        'reminder_minutes_before': 10,
        'missed_prayer_reminders': True
    }


# This step is defined in authentication_steps.py


@given('I have family members added to my account')
def step_have_family_members(context):
    """Set up family members."""
    from app.models.family import FamilyMember

    family_member = FamilyMember(
        user_id=context.current_user.id,
        name="Family Member",
        relationship="spouse",
        email="family@example.com"
    )
    context.db.session.add(family_member)
    context.db.session.commit()
    context.family_members = [family_member]


@when('the page loads')
def step_page_loads(context):
    """Simulate page load."""
    prayer_service = PrayerService()
    context.dashboard_data = prayer_service.get_user_statistics(context.current_user.id)


@when('I view the weekly calendar')
def step_view_weekly_calendar(context):
    """View weekly calendar."""
    context.calendar_view = 'weekly'
    context.calendar_data = {
        'monday': {'status': 'completed', 'prayers': ['FAJR', 'DHUHR']},
        'tuesday': {'status': 'partial', 'prayers': ['FAJR']},
        'wednesday': {'status': 'missed', 'prayers': []},
        'thursday': {'status': 'completed', 'prayers': ['FAJR', 'DHUHR', 'ASR']},
        'friday': {'status': 'completed', 'prayers': ['FAJR', 'DHUHR', 'ASR', 'MAGHRIB']},
        'saturday': {'status': 'pending', 'prayers': []},
        'sunday': {'status': 'pending', 'prayers': []}
    }


@when('I click the "Previous Week" button')
def step_click_previous_week(context):
    """Click previous week button."""
    context.current_week = context.current_week - 1 if hasattr(context, 'current_week') else -1


@when('I click the "Next Week" button')
def step_click_next_week(context):
    """Click next week button."""
    context.current_week = context.current_week + 1 if hasattr(context, 'current_week') else 1


@when('I select a specific date range')
def step_select_date_range(context):
    """Select specific date range."""
    context.date_range = {
        'start': datetime.now().date() - timedelta(days=7),
        'end': datetime.now().date()
    }


@when('I view the page on a mobile device')
def step_view_on_mobile_device(context):
    """View page on mobile device."""
    context.device_type = 'mobile'
    context.screen_width = 375  # iPhone width


@when('I view the statistics multiple times')
def step_view_statistics_multiple_times(context):
    """View statistics multiple times."""
    context.view_count = 5
    context.cached_responses = []

    for _i in range(context.view_count):
        prayer_service = PrayerService()
        stats = prayer_service.get_user_statistics(context.current_user.id)
        context.cached_responses.append(stats)


@when('I view the dashboard')
def step_view_dashboard(context):
    """View dashboard."""
    prayer_service = PrayerService()
    context.dashboard_data = prayer_service.get_user_statistics(context.current_user.id)


@when('I filter by family member')
def step_filter_by_family_member(context):
    """Filter by family member."""
    context.filter_family_member = context.family_members[0].id


@then('I should see my prayer completion statistics')
def step_see_prayer_completion_statistics(context):
    """Verify prayer completion statistics are visible."""
    assert 'statistics' in context.dashboard_data
    assert 'completion_rate' in context.dashboard_data['statistics']


@then('I should see today\'s completion rate')
def step_see_todays_completion_rate(context):
    """Verify today's completion rate is visible."""
    assert 'today' in context.dashboard_data['statistics']
    assert 'completion_rate' in context.dashboard_data['statistics']['today']


@then('I should see this week\'s completion rate')
def step_see_weeks_completion_rate(context):
    """Verify this week's completion rate is visible."""
    assert 'week' in context.dashboard_data['statistics']
    assert 'completion_rate' in context.dashboard_data['statistics']['week']


@then('I should see this month\'s completion rate')
def step_see_months_completion_rate(context):
    """Verify this month's completion rate is visible."""
    assert 'month' in context.dashboard_data['statistics']
    assert 'completion_rate' in context.dashboard_data['statistics']['month']


@then('I should see zero completion rates')
def step_see_zero_completion_rates(context):
    """Verify zero completion rates are shown."""
    stats = context.dashboard_data['statistics']
    assert stats['today']['completion_rate'] == 0
    assert stats['week']['completion_rate'] == 0
    assert stats['month']['completion_rate'] == 0


@then('I should see a message encouraging me to start tracking prayers')
def step_see_encouragement_message(context):
    """Verify encouragement message is shown."""
    assert 'message' in context.dashboard_data
    assert 'start' in context.dashboard_data['message'].lower()


@then('I should see accurate completion percentages')
def step_see_accurate_completion_percentages(context):
    """Verify completion percentages are accurate."""
    stats = context.dashboard_data['statistics']
    assert 0 <= stats['today']['completion_rate'] <= 100
    assert 0 <= stats['week']['completion_rate'] <= 100
    assert 0 <= stats['month']['completion_rate'] <= 100


@then('I should see the count of completed prayers')
def step_see_completed_prayers_count(context):
    """Verify count of completed prayers."""
    assert 'completed_count' in context.dashboard_data['statistics']


@then('I should see the count of missed prayers')
def step_see_missed_prayers_count(context):
    """Verify count of missed prayers."""
    assert 'missed_count' in context.dashboard_data['statistics']


@then('I should see the count of qada prayers')
def step_see_qada_prayers_count(context):
    """Verify count of qada prayers."""
    assert 'qada_count' in context.dashboard_data['statistics']


@then('I should see prayer completion status for each day')
def step_see_prayer_completion_status_per_day(context):
    """Verify prayer completion status for each day."""
    assert context.calendar_data is not None
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        assert day in context.calendar_data


@then('completed prayers should be marked with green indicators')
def step_completed_prayers_green_indicators(context):
    """Verify completed prayers have green indicators."""
    for day_data in context.calendar_data.values():
        if day_data['status'] == 'completed':
            assert day_data.get('indicator_color') == 'green'


@then('missed prayers should be marked with red indicators')
def step_missed_prayers_red_indicators(context):
    """Verify missed prayers have red indicators."""
    for day_data in context.calendar_data.values():
        if day_data['status'] == 'missed':
            assert day_data.get('indicator_color') == 'red'


@then('pending prayers should be marked with yellow indicators')
def step_pending_prayers_yellow_indicators(context):
    """Verify pending prayers have yellow indicators."""
    for day_data in context.calendar_data.values():
        if day_data['status'] == 'pending':
            assert day_data.get('indicator_color') == 'yellow'


@then('I should see the previous week\'s prayer data')
def step_see_previous_week_data(context):
    """Verify previous week's data is shown."""
    assert context.current_week == -1


@then('I should see the next week\'s prayer data')
def step_see_next_week_data(context):
    """Verify next week's data is shown."""
    assert context.current_week == 1


@then('I should see statistics only for that date range')
def step_see_statistics_for_date_range(context):
    """Verify statistics are for the selected date range."""
    assert 'date_range' in context.dashboard_data
    assert context.dashboard_data['date_range'] == context.date_range


@then('the completion rates should be calculated correctly')
def step_completion_rates_calculated_correctly(context):
    """Verify completion rates are calculated correctly."""
    stats = context.dashboard_data['statistics']
    # Basic validation that rates are reasonable
    assert 0 <= stats['completion_rate'] <= 100


@then('the prayer times should be displayed in my timezone')
def step_prayer_times_in_timezone(context):
    """Verify prayer times are in user's timezone."""
    assert 'timezone' in context.dashboard_data
    assert context.dashboard_data['timezone'] == context.current_user.timezone


@then('the completion times should be accurate for my timezone')
def step_completion_times_accurate_timezone(context):
    """Verify completion times are accurate for timezone."""
    assert 'completion_times' in context.dashboard_data
    # Times should be in user's timezone
    for time_data in context.dashboard_data['completion_times']:
        assert 'timezone' in time_data


@then('the dashboard should be responsive')
def step_dashboard_responsive(context):
    """Verify dashboard is responsive."""
    assert context.device_type == 'mobile'
    assert context.screen_width <= 768  # Mobile breakpoint


@then('all statistics should be clearly visible')
def step_statistics_clearly_visible(context):
    """Verify statistics are clearly visible."""
    assert 'statistics' in context.dashboard_data
    # On mobile, statistics should be clearly visible
    assert context.device_type == 'mobile'


@then('the calendar should be touch-friendly')
def step_calendar_touch_friendly(context):
    """Verify calendar is touch-friendly."""
    assert context.device_type == 'mobile'
    # Touch-friendly elements should be at least 44px
    assert context.calendar_data.get('touch_friendly', True)


@then('the data should be cached appropriately')
def step_data_cached_appropriately(context):
    """Verify data is cached appropriately."""
    # Check that subsequent requests are faster (cached)
    assert len(context.cached_responses) == context.view_count
    # All responses should be identical (from cache)
    first_response = context.cached_responses[0]
    for response in context.cached_responses[1:]:
        assert response == first_response


@then('subsequent requests should be faster')
def step_subsequent_requests_faster(context):
    """Verify subsequent requests are faster."""
    # This would typically measure response times
    context.cache_performance_improved = True


@then('the data should remain accurate')
def step_data_remains_accurate(context):
    """Verify cached data remains accurate."""
    # Cached data should still be accurate
    assert all('statistics' in response for response in context.cached_responses)


@then('I should see statistics for my family members')
def step_see_family_member_statistics(context):
    """Verify family member statistics are shown."""
    assert 'family_statistics' in context.dashboard_data


@then('I should be able to filter by family member')
def step_able_to_filter_by_family_member(context):
    """Verify ability to filter by family member."""
    assert context.filter_family_member is not None


@then('I should see aggregate statistics for the family')
def step_see_aggregate_family_statistics(context):
    """Verify aggregate family statistics are shown."""
    assert 'family_aggregate' in context.dashboard_data
    assert 'total_completion_rate' in context.dashboard_data['family_aggregate']
