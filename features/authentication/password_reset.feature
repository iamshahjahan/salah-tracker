Feature: Password Reset
  As a user who forgot their password
  I want to reset my password using my email
  So that I can regain access to my account

  Background:
    Given the application is running
    And the database is clean
    And a user with email "test@example.com" and password "oldpassword123" exists

  @smoke @api
  Scenario: Successful password reset flow
    Given I am on the login page
    When I click "Forgot Password"
    And I enter my email for password reset "test@example.com"
    And I submit the forgot password form
    Then I should receive a password reset email
    And I should see a success message

  @smoke @api
  Scenario: Reset password with valid code
    Given I have a valid password reset code for "test@example.com"
    When I navigate to the reset password page with the code
    And I enter a new password "newpassword123"
    And I confirm the new password "newpassword123"
    And I submit the reset password form
    Then my password should be reset successfully
    And I should be able to login with the new password

  @smoke @api
  Scenario: Reset password with invalid code
    Given I have an invalid password reset code
    When I navigate to the reset password page with the code
    Then I should see an error message about invalid code

  @smoke @api
  Scenario: Reset password with expired code
    Given I have an expired password reset code for "test@example.com"
    When I navigate to the reset password page with the code
    Then I should see an error message about expired code

