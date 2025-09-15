Feature: Time-Based Prayer State Transitions
  As a Muslim user
  I want to understand how prayer states change based on time
  So that I can track my prayers accurately according to Islamic timing

  Background:
    Given the application is running
    Given I am logged in as a user with timezone "Asia/Kolkata"


  @smoke @api @time-based
  Scenario: Fajr prayer state transitions throughout the day
    # Before Fajr time (04:00)
    Given I am checking the namaz times of 2025-09-16 at time 2025-09-16 12:10
    Then All the namaz should be in future
#    And I should not be able to mark Fajr as qada

#    # At Fajr time (05:21)
#    Given the current time is "05:21" in my timezone
#    When I check the Fajr prayer status
#    Then the Fajr prayer should be in "pending" state
#    And I should be able to complete the Fajr prayer
#    And I should not be able to mark Fajr as qada
#
#    # During Fajr window (06:30)
#    Given the current time is "06:30" in my timezone
#    When I check the Fajr prayer status
#    Then the Fajr prayer should be in "pending" state
#    And I should be able to complete the Fajr prayer
#    And I should not be able to mark Fajr as qada
#
#    # After Fajr window but before Dhuhr (10:00)
#    Given the current time is "10:00" in my timezone
#    When I check the Fajr prayer status
#    Then the Fajr prayer should be in "missed" state
#    And I should not be able to complete the Fajr prayer
#    And I should be able to mark Fajr as qada

  @api @time-based
  Scenario: Dhuhr prayer state transitions throughout the day
    # Before Dhuhr time (11:00)
    Given the current time is "11:00" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "future" state
    And I should not be able to complete the Dhuhr prayer
    And I should not be able to mark Dhuhr as qada

    # At Dhuhr time (12:15)
    Given the current time is "12:15" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And I should be able to complete the Dhuhr prayer
    And I should not be able to mark Dhuhr as qada

    # During Dhuhr window (14:00)
    Given the current time is "14:00" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And I should be able to complete the Dhuhr prayer
    And I should not be able to mark Dhuhr as qada

    # At Asr time (15:45) - Dhuhr window ends
    Given the current time is "15:45" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "missed" state
    And I should not be able to complete the Dhuhr prayer
    And I should be able to mark Dhuhr as qada

  @api @time-based
  Scenario: Asr prayer state transitions throughout the day
    # Before Asr time (14:00)
    Given the current time is "14:00" in my timezone
    When I check the Asr prayer status
    Then the Asr prayer should be in "future" state
    And I should not be able to complete the Asr prayer
    And I should not be able to mark Asr as qada

    # At Asr time (15:45)
    Given the current time is "15:45" in my timezone
    When I check the Asr prayer status
    Then the Asr prayer should be in "pending" state
    And I should be able to complete the Asr prayer
    And I should not be able to mark Asr as qada

    # During Asr window (17:00)
    Given the current time is "17:00" in my timezone
    When I check the Asr prayer status
    Then the Asr prayer should be in "pending" state
    And I should be able to complete the Asr prayer
    And I should not be able to mark Asr as qada

    # At Maghrib time (18:30) - Asr window ends
    Given the current time is "18:30" in my timezone
    When I check the Asr prayer status
    Then the Asr prayer should be in "missed" state
    And I should not be able to complete the Asr prayer
    And I should be able to mark Asr as qada

  @api @time-based
  Scenario: Maghrib prayer state transitions throughout the day
    # Before Maghrib time (17:00)
    Given the current time is "17:00" in my timezone
    When I check the Maghrib prayer status
    Then the Maghrib prayer should be in "future" state
    And I should not be able to complete the Maghrib prayer
    And I should not be able to mark Maghrib as qada

    # At Maghrib time (18:30)
    Given the current time is "18:30" in my timezone
    When I check the Maghrib prayer status
    Then the Maghrib prayer should be in "pending" state
    And I should be able to complete the Maghrib prayer
    And I should not be able to mark Maghrib as qada

    # During Maghrib window (19:00)
    Given the current time is "19:00" in my timezone
    When I check the Maghrib prayer status
    Then the Maghrib prayer should be in "pending" state
    And I should be able to complete the Maghrib prayer
    And I should not be able to mark Maghrib as qada

    # At Isha time (19:45) - Maghrib window ends
    Given the current time is "19:45" in my timezone
    When I check the Maghrib prayer status
    Then the Maghrib prayer should be in "missed" state
    And I should not be able to complete the Maghrib prayer
    And I should be able to mark Maghrib as qada

  @api @time-based
  Scenario: Isha prayer state transitions throughout the day
    # Before Isha time (18:00)
    Given the current time is "18:00" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "future" state
    And I should not be able to complete the Isha prayer
    And I should not be able to mark Isha as qada

    # At Isha time (19:45)
    Given the current time is "19:45" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer
    And I should not be able to mark Isha as qada

    # During Isha window (22:00)
    Given the current time is "22:00" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer
    And I should not be able to mark Isha as qada

    # Late night (23:30)
    Given the current time is "23:30" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer
    And I should not be able to mark Isha as qada

    # Next day before Fajr (03:00)
    Given the current time is "03:00" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "missed" state
    And I should not be able to complete the Isha prayer
    And I should be able to mark Isha as qada

  @api @time-based @completion
  Scenario: Prayer completion state transitions
    # Complete Fajr during its window
    Given the current time is "06:00" in my timezone
    And the Fajr prayer is in "pending" state
    When I mark the Fajr prayer as completed
    Then the Fajr prayer should be in "completed" state
    And I should not be able to complete the Fajr prayer again
    And I should not be able to mark Fajr as qada

    # Try to complete Dhuhr after its window
    Given the current time is "16:00" in my timezone
    And the Dhuhr prayer is in "missed" state
    When I try to mark the Dhuhr prayer as completed
    Then I should see an error message "Cannot complete prayer outside time window"
    And the Dhuhr prayer should remain in "missed" state

    # Mark missed Dhuhr as qada
    Given the current time is "16:00" in my timezone
    And the Dhuhr prayer is in "missed" state
    When I mark the Dhuhr prayer as qada
    Then the Dhuhr prayer should be in "qada" state
    And I should not be able to complete the Dhuhr prayer
    And I should not be able to mark Dhuhr as qada again

  @api @time-based @timezone
  Scenario: Timezone-aware prayer state transitions
    # User in New York timezone
    Given I am logged in as a user with timezone "America/New_York"
    And the current time is "07:00" in my timezone
    When I check the Fajr prayer status
    Then the Fajr prayer should be in "pending" state
    And the prayer time should be displayed in "America/New_York" timezone

    # User in London timezone
    Given I am logged in as a user with timezone "Europe/London"
    And the current time is "12:00" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And the prayer time should be displayed in "Europe/London" timezone

    # User in Dubai timezone
    Given I am logged in as a user with timezone "Asia/Dubai"
    And the current time is "18:00" in my timezone
    When I check the Maghrib prayer status
    Then the Maghrib prayer should be in "pending" state
    And the prayer time should be displayed in "Asia/Dubai" timezone

  @api @time-based @edge-cases
  Scenario: Edge cases for prayer state transitions
    # Exactly at prayer start time
    Given the current time is "12:15:00" in my timezone with seconds
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And I should be able to complete the Dhuhr prayer

    # Exactly at prayer end time
    Given the current time is "15:45:00" in my timezone with seconds
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And I should be able to complete the Dhuhr prayer

    # One second after prayer end time
    Given the current time is "15:45:01" in my timezone with seconds
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "missed" state
    And I should not be able to complete the Dhuhr prayer

    # One second before prayer start time
    Given the current time is "12:14:59" in my timezone with seconds
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "future" state
    And I should not be able to complete the Dhuhr prayer

  @api @time-based @midnight
  Scenario: Midnight prayer state transitions
    # Late night Isha completion
    Given the current time is "23:59" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer

    # Early morning before Fajr
    Given the current time is "00:30" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer

    # Very early morning (2 AM)
    Given the current time is "02:00" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "pending" state
    And I should be able to complete the Isha prayer

    # Just before Fajr (5 AM)
    Given the current time is "05:20" in my timezone
    When I check the Isha prayer status
    Then the Isha prayer should be in "missed" state
    And I should not be able to complete the Isha prayer

  @api @time-based @daylight-savings
  Scenario: Daylight savings time prayer state transitions
    # During daylight savings transition
    Given I am logged in as a user with timezone "America/New_York"
    And it is daylight savings time
    And the current time is "12:00" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And the prayer time should account for daylight savings

    # After daylight savings ends
    Given I am logged in as a user with timezone "America/New_York"
    And daylight savings has ended
    And the current time is "12:00" in my timezone
    When I check the Dhuhr prayer status
    Then the Dhuhr prayer should be in "pending" state
    And the prayer time should account for standard time
