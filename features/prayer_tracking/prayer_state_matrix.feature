Feature: Prayer State Matrix - Comprehensive Date and Time Validation
  As a Muslim user
  I want to validate prayer states across different dates and times
  So that I can ensure accurate prayer tracking in all scenarios

  Background:
    Given the application is running
    Given I am logged in as a user with timezone "Asia/Kolkata" and created_at 2020-01-01 03:00

  @smoke @api @matrix @comprehensive
  Scenario Outline: Prayer state validation matrix
    Given I am checking the prayer times of "<date>" at time "<datetime>"
    Then the Fajr prayer should be in "<fajr_state>" state
    And the Dhuhr prayer should be in "<dhuhr_state>" state
    And the Asr prayer should be in "<asr_state>" state
    And the Maghrib prayer should be in "<maghrib_state>" state
    And the Isha prayer should be in "<isha_state>" state

    Examples: Prayer States Matrix
      | timezone        | date       | datetime            | fajr_state | dhuhr_state | asr_state | maghrib_state | isha_state |
      # Summer Solstice (Longest Day) - June 21, 2025
      | Asia/Kolkata    | 2025-06-21 | 2025-06-20 04:30    | future     | future      | future    | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 05:00    | pending    | future      | future    | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 07:00    | missed    | future      | future    | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 13:00    | missed    | pending     | future    | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 14:00    | missed    | pending     | future    | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 16:00    | missed    | missed     | pending   | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 17:00    | missed    | missed     | pending   | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 18:00    | missed    | missed     | missed   | future        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 19:00    | missed    | missed     | missed   | pending        | future     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 20:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 21:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 22:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 23:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-22 00:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-22 01:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-22 02:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-22 03:00    | missed    | missed     | missed   | missed        | pending     |
      | Asia/Kolkata    | 2025-06-21 | 2025-06-22 04:00    | missed    | missed     | missed   | missed        | pending     |

#
#      # Winter Solstice (Shortest Day) - December 21, 2025
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 04:00    | future     | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 05:00    | future     | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 06:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 07:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 08:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 09:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 10:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 11:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 12:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 12:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 13:00    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 14:00    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 15:00    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 15:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 16:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 17:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 18:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 20:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 21:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 22:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-12-21 | 2025-12-21 23:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Spring Equinox - March 20, 2025
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 03:30    | future     | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 05:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 12:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 12:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 15:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 16:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 18:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-03-20 | 2025-03-20 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Fall Equinox - September 22, 2025
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 04:00    | future     | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 05:30    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 12:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 12:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 15:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 16:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 18:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-09-22 | 2025-09-22 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Different Timezones - New York (EST/EDT)
#      | America/New_York| 2025-06-21 | 2025-06-21 03:00    | future     | future      | future    | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 05:00    | pending    | future      | future    | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 12:00    | pending    | future      | future    | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 12:30    | pending    | pending     | future    | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 15:30    | pending    | pending     | future    | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 16:00    | pending    | pending     | pending   | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 18:00    | pending    | pending     | pending   | future        | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 18:30    | pending    | pending     | pending   | pending       | future     |
#      | America/New_York| 2025-06-21 | 2025-06-21 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | America/New_York| 2025-06-21 | 2025-06-21 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Different Timezones - London (GMT/BST)
#      | Europe/London   | 2025-06-21 | 2025-06-21 02:00    | future     | future      | future    | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 04:00    | pending    | future      | future    | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 12:00    | pending    | future      | future    | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 12:30    | pending    | pending     | future    | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 15:30    | pending    | pending     | future    | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 16:00    | pending    | pending     | pending   | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 18:00    | pending    | pending     | pending   | future        | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Europe/London   | 2025-06-21 | 2025-06-21 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Europe/London   | 2025-06-21 | 2025-06-21 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Different Timezones - Dubai (GST)
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 03:00    | future     | future      | future    | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 05:00    | pending    | future      | future    | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 12:00    | pending    | future      | future    | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 12:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 15:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 16:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 18:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Dubai      | 2025-06-21 | 2025-06-21 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Edge Cases - Midnight Transitions
#      | Asia/Kolkata    | 2025-06-21 | 2025-06-21 23:59    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 00:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 00:30    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 01:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 02:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 03:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 04:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 05:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 05:30    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-06-22 | 2025-06-22 06:00    | pending    | future      | future    | future        | future     |
#
#      # Edge Cases - Leap Year
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 05:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 12:00    | pending    | future      | future    | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 12:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 15:30    | pending    | pending     | future    | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 16:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 18:00    | pending    | pending     | pending   | future        | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 18:30    | pending    | pending     | pending   | pending       | future     |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 19:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2024-02-29 | 2024-02-29 20:00    | pending    | pending     | pending   | pending       | pending    |
#
#      # Edge Cases - Year End/Start
#      | Asia/Kolkata    | 2024-12-31 | 2024-12-31 23:59    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 00:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 00:30    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 01:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 02:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 03:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 04:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 05:00    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 05:30    | pending    | pending     | pending   | pending       | pending    |
#      | Asia/Kolkata    | 2025-01-01 | 2025-01-01 06:00    | pending    | future      | future    | future        | future     |