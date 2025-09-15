Feature: Prayer Completion
  As a logged-in user
  I want to mark my prayers as completed
  So that I can track my prayer consistency

  Background:
    Given the application is running
    And I am logged in as a user
    And today's prayer times are available

  @smoke @api
  Scenario: Complete prayer during prayer time window
    Given it is currently within the Dhuhr prayer time window
    When I mark the Dhuhr prayer as completed
    Then the prayer should be marked as "completed"
    And I should see a success message
    And the prayer status should be updated in real-time
#
#  @api
#  Scenario: Complete prayer after prayer time window
#    Given the Dhuhr prayer time window has passed
#    When I mark the Dhuhr prayer as completed
#    Then the prayer should be marked as "qada"
#    And I should see a message about completing missed prayer
#    And the prayer status should be updated accordingly
#
#  @api
#  Scenario: Complete prayer before prayer time window
#    Given it is before the Dhuhr prayer time window
#    When I try to mark the Dhuhr prayer as completed
#    Then I should see an error message "Cannot complete prayer yet"
#    And the prayer should remain in "pending" status
#
#  @api
#  Scenario: Complete prayer with timezone awareness
#    Given I am in timezone "Asia/Kolkata"
#    And the current time is "14:30" in my timezone
#    And the Dhuhr prayer time is "12:15" in my timezone
#    When I mark the Dhuhr prayer as completed
#    Then the prayer should be marked as "completed"
#    And the completion time should be recorded correctly
#
#  @ui
#  Scenario: Prayer completion via UI
#    Given I am on the prayers page
#    And I can see today's prayer times
#    When I click the "Mark as Complete" button for Dhuhr prayer
#    Then the button should change to "Completed"
#    And the prayer card should show completed status
#    And I should see a success notification
#
#  @ui
#  Scenario: Prayer completion via completion link
#    Given I have received a prayer completion link via email
#    When I click the completion link
#    Then I should be taken to the prayer completion page
#    And I should see the prayer details
#    When I click "Mark as Complete"
#    Then the prayer should be marked as completed
#    And I should see a success page
#
#  @api
#  Scenario: Prayer completion with notes
#    Given it is within the Dhuhr prayer time window
#    When I mark the Dhuhr prayer as completed
#    And I add a note "Prayed at mosque"
#    Then the prayer should be marked as "completed"
#    And the note should be saved
#    And I should be able to view the note later
#
#  @api
#  Scenario: Prayer completion validation
#    Given I am logged in
#    When I try to complete a prayer without proper authentication
#    Then I should see an authentication error
#    And the prayer should not be completed
#
#  @api
#  Scenario: Prayer completion for non-existent prayer
#    Given I am logged in
#    When I try to complete a prayer that doesn't exist
#    Then I should see an error message "Prayer not found"
#    And no completion should be recorded
#
#  @api
#  Scenario: Prayer completion rate limiting
#    Given I am logged in
#    When I try to complete the same prayer multiple times rapidly
#    Then I should be rate limited
#    And I should see an error message about too many requests
