Feature: Email Verification
  As a registered user
  I want to verify my email address
  So that I can receive prayer reminders and notifications

  Background:
    Given the application is running
    And a user with unverified email exists

  @smoke @api
  Scenario: Successful email verification
    Given I am a registered user with unverified email
    And I have received a verification email
    When I enter the correct verification code
    And I submit the verification form
    Then my email should be verified
    And I should see a success message
    And the email verification header should disappear

  @api
  Scenario: Email verification with incorrect code
    Given I am a registered user with unverified email
    When I enter an incorrect verification code
    And I submit the verification form
    Then I should see an error message "Invalid verification code"
    And my email should remain unverified

  @api
  Scenario: Email verification with expired code
    Given I am a registered user with unverified email
    And I have an expired verification code
    When I enter the expired verification code
    And I submit the verification form
    Then I should see an error message "Verification code has expired"
    And my email should remain unverified

  @api
  Scenario: Resend verification code
    Given I am a registered user with unverified email
    When I click "Resend Code"
    Then I should receive a new verification email
    And I should see a confirmation message
    And the previous verification code should be invalidated


  @api
  Scenario: Automatic email verification during registration
    Given I am registering a new account
    When I complete the registration process
    Then an email verification should be automatically sent

  @api
  Scenario: Email verification for already verified user
    Given I am a registered user with verified email
    When I try to verify my email again
    Then I should see an error message "Email is already verified"
    And no new verification code should be sent
