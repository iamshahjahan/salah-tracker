Feature: Prayer Completion
  As a logged-in user
  I want to mark my prayers as completed
  So that I can track my prayer consistency

  Background:
    Given the application is running
#    todo move this in common method
    Given I am logged in as a user with timezone "Asia/Kolkata" and created_at 2020-01-01 03:00

  @smoke @api @matrix @comprehensive
  Scenario Outline: Mark Prayer Completion
    Given I am checking the prayer times of "<date>" at time "<datetime>"
    When I mark the "<valid_prayer>" prayer as completed
#    todo fix this jamaat from UI
    Then the prayer should be marked as "jamaat"
    When I mark the "<valid_prayer>" prayer as completed
    Then I should see an error message "Prayer already completed"
    Examples: Prayer States Matrix
      | timezone     | date       | datetime         | valid_prayer |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 05:30 | Fajr         |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 13:00 | Dhuhr        |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 16:30 | Asr          |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 19:00 | Maghrib      |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 21:00 | Isha         |

  @smoke @api @matrix @comprehensive
  Scenario Outline: Mark Valid Prayer Qada
    Given I am checking the prayer times of "<date>" at time "<datetime>"
    When I mark the "<valid_prayer>" prayer as qada
#    todo fix this jamaat from UI
    Then the prayer should be marked as "qada"
    When I mark the "<valid_prayer>" prayer as completed
    Then I should see an error message "Prayer already completed"
    Examples: Prayer States Matrix
      | timezone     | date       | datetime         | valid_prayer |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 07:30 | Fajr         |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 16:00 | Dhuhr        |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 19:30 | Asr          |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 21:00 | Maghrib      |
      | Asia/Kolkata | 2025-06-21 | 2025-06-22 21:00 | Isha         |


  @smoke @api @matrix @comprehensive
  Scenario Outline: Mark Invalid Prayer Qada
    Given I am checking the prayer times of "<date>" at time "<datetime>"
    When I mark the "<in_valid_prayer>" prayer as qada
#    todo fix this jamaat from UI
    Then I should see an error message "Can not mark as Qada"

    Examples: Prayer States Matrix
      | timezone     | date       | datetime         | in_valid_prayer |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 07:30 | Dhuhr        |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 16:00 | Asr          |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 19:00 | Maghrib      |
      | Asia/Kolkata | 2025-06-21 | 2025-06-21 21:00 | Isha         |
