Feature: Prayer Reminders
  As a registered user
  I want to receive prayer reminders
  So that I don't miss my prayers

  Background:
    Given the application is running
    And I am a registered user with verified email
    And I have set my prayer reminder preferences

  @smoke @api
  Scenario: Receive prayer reminder before prayer time
    Given it is 10 minutes before Dhuhr prayer time
    When the reminder system runs
    Then I should receive a prayer reminder email
#    And the email should contain the prayer name and time
#    And the email should contain a completion link

  @api
  Scenario: Receive prayer reminder for missed prayer
    Given the Dhuhr prayer time has passed
    And I have not completed the prayer
    When the reminder system runs
    Then I should receive a missed prayer reminder
#    And the email should contain a completion link for qada

  @api
  Scenario: Do not receive reminder for completed prayer
    Given I have already completed the Dhuhr prayer
    When the reminder system runs
    Then I should not receive a prayer reminder

#  @api
#  Scenario: Receive reminder with correct timezone
#    Given I am in timezone "Asia/Kolkata"
#    And it is 10 minutes before Dhuhr prayer time in my timezone
#    When the reminder system runs
#    Then I should receive a prayer reminder
#    And the prayer time should be displayed in my timezone

#  @api
#  Scenario: Receive reminder with family member information
#    Given I have family members added to my account
#    And it is 10 minutes before Dhuhr prayer time
#    When the reminder system runs
#    Then I should receive a prayer reminder
#    And the email should include family member prayer status
#
#  @api
#  Scenario: Reminder rate limiting
#    Given I have requested multiple reminders rapidly
#    When I try to request another reminder
#    Then I should be rate limited
#    And I should see an error message about too many requests
#
#  @ui
#  Scenario: Configure reminder preferences
#    Given I am on the settings page
#    When I configure my reminder preferences
#    Then my preferences should be saved
#    And I should see a confirmation message

#  @ui
#  Scenario: Disable prayer reminders
#    Given I am on the settings page
#    When I disable prayer reminders
#    Then I should not receive any prayer reminders
#    And my preference should be saved
#
#  @api
#  Scenario: Reminder delivery failure handling
#    Given my email address is invalid
#    When the reminder system tries to send a reminder
#    Then the delivery should fail gracefully
#    And the failure should be logged
#    And I should not receive the reminder

#  @api
#  Scenario: Bulk reminder processing
#    Given there are 100 users who need reminders
#    When the reminder system processes all users
#    Then all users should receive their reminders
#    And the processing should complete within 5 minutes
