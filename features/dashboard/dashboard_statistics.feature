Feature: Dashboard Statistics
  As a logged-in user
  I want to view my prayer statistics
  So that I can track my prayer consistency and progress

  Background:
    Given the application is running
    Given I am logged in as a user with timezone "Asia/Kolkata" and created_at 2025-01-01 03:00

  @smoke @api @matrix @comprehensive
  Scenario Outline: Statistics for 2 days with mixed completion states
    Given I am checking the prayer times of "<date1>" at time "<datetime1>"
    And I am completing prayers as qada at time "<datetime1>"
    And I am completing prayers at time "<datetime1>"
    And I am checking the prayer times of "<date2>" at time "<datetime2>"
    And I am completing prayers as qada at time "<datetime2>"
    And I am completing prayers at time "<datetime2>"
    When the page loads
    Then I should see my prayer completion statistics
    And the overall statistics should be accurate
    And the daily statistics should be accurate
    And the prayer-specific statistics should be accurate

    Examples: Prayer States Matrix
      | date1       | datetime1       | date2      |  datetime2       |
      | 2025-06-21 | 2025-06-22 20:00 | 2025-06-22 | 2025-06-22 20:00 |
