#Feature: Dashboard Statistics
#  As a logged-in user
#  I want to view my prayer statistics
#  So that I can track my prayer consistency and progress
#
#  Background:
#    Given the application is running
#    And I am logged in as a user
#    And I have prayer completion history
#
#  @smoke @api
#  Scenario: View dashboard statistics
#    Given I am on the dashboard page
#    When the page loads
#    Then I should see my prayer completion statistics
#    And I should see today's completion rate
#    And I should see this week's completion rate
#    And I should see this month's completion rate
#
#  @api
#  Scenario: Dashboard statistics with no prayer history
#    Given I am a new user with no prayer completions
#    When I navigate to the dashboard
#    Then I should see zero completion rates
#    And I should see a message encouraging me to start tracking prayers
#
#  @api
#  Scenario: Dashboard statistics with mixed completion status
#    Given I have completed some prayers and missed others
#    When I view the dashboard statistics
#    Then I should see accurate completion percentages
#    And I should see the count of completed prayers
#    And I should see the count of missed prayers
#    And I should see the count of qada prayers
#
#  @ui
#  Scenario: Dashboard calendar view
#    Given I am on the dashboard page
#    When I view the weekly calendar
#    Then I should see prayer completion status for each day
#    And completed prayers should be marked with green indicators
#    And missed prayers should be marked with red indicators
#    And pending prayers should be marked with yellow indicators
#
#  @ui
#  Scenario: Dashboard navigation between weeks
#    Given I am on the dashboard page
#    When I click the "Previous Week" button
#    Then I should see the previous week's prayer data
#    When I click the "Next Week" button
#    Then I should see the next week's prayer data
#
#  @api
#  Scenario: Dashboard statistics for specific date range
#    Given I am on the dashboard page
#    When I select a specific date range
#    Then I should see statistics only for that date range
#    And the completion rates should be calculated correctly
#
#  @api
#  Scenario: Dashboard statistics with timezone handling
#    Given I am in timezone "Asia/Kolkata"
#    When I view the dashboard statistics
#    Then the prayer times should be displayed in my timezone
#    And the completion times should be accurate for my timezone
#
#  @ui
#  Scenario: Dashboard responsive design
#    Given I am on the dashboard page
#    When I view the page on a mobile device
#    Then the dashboard should be responsive
#    And all statistics should be clearly visible
#    And the calendar should be touch-friendly
#
#  @api
#  Scenario: Dashboard statistics caching
#    Given I am on the dashboard page
#    When I view the statistics multiple times
#    Then the data should be cached appropriately
#    And subsequent requests should be faster
#    And the data should remain accurate
#
#  @api
#  Scenario: Dashboard statistics with family members
#    Given I have family members added to my account
#    When I view the dashboard
#    Then I should see statistics for my family members
#    And I should be able to filter by family member
#    And I should see aggregate statistics for the family
