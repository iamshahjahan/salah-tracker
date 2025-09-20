#Feature: Prayer Reminders
#  As a registered user
#  I want to receive prayer reminders
#  So that I don't miss my prayers
#
#  Background:
#    Given the application is running
#    And I am a registered user with verified email
#    And I have set my prayer reminder preferences
#
#  @smoke @api
#  Scenario: Receive prayer reminder before prayer time
#    Given it is 10 minutes before Dhuhr prayer time
#    When the reminder system runs
#    Then I should receive a prayer reminder email
#    And the email should contain the prayer name and time
#    And the email should contain a completion link

Feature: Prayer Reminders 2
  I want to validate prayer states across different dates and times
  So that I can ensure accurate prayer tracking in all scenarios

  Background:
    Given the application is running
    Given I am logged in as a user with timezone "Asia/Kolkata" and created_at 2020-01-01 03:00


  @smoke @api @matrix @comprehensive
  Scenario Outline: Prayer state validation matrix
    Given I am checking the prayer times of "<date>" at time "<datetime>"
    Then I am sending a reminder for the user at "<datetime>"
    Then There should be "1" notification
    Then I am sending a reminder for the user at "<datetime>"
    Then There should be "0" notification

    Examples: Prayer States Matrix
  | timezone     | date       | datetime         |
  # Summer Solstice (Longest Day) - June 21, 2025
  | Asia/Kolkata | 2025-06-21 | 2025-06-21 05:00 |
  | Asia/Kolkata | 2025-06-21 | 2025-06-21 13:00 |
  | Asia/Kolkata | 2025-06-21 | 2025-06-21 17:00 |
  | Asia/Kolkata | 2025-06-21 | 2025-06-21 19:00 |
  | Asia/Kolkata | 2025-06-21 | 2025-06-21 20:00 |
