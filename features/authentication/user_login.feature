Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access my prayer tracking features

  Background:
    Given the application is running
    And a user with email "testuser@example.com" and password "password123" exists

  @smoke @api
  Scenario: Successful login with username and password
    Given I am on the login page
    When I enter email "testuser@example.com"
    And I enter password "password123"
    And I click the login button with email
    Then I should be logged in successfully
    And I should be redirected to the prayers page
    And I should see my user profile information

  @api
  Scenario: Login with OTP
    Given I am on the login page
    When I switch to OTP login tab
    And I enter my email "testuser@example.com"
    And I click "Send Code"
    Then I should receive an OTP code via email
    When I enter the OTP code
    And I click "Login with Code"
#    todo :: fix this
#    Then I should be logged in successfully

  @api
  Scenario: Failed login with incorrect password
    Given I am on the login page
    When I enter email "testuser@example.com"
    And I enter password "wrongpassword"
    And I click the login button with email
    Then I should see an error message "Invalid email or password"
    And I should not be logged in

  @api
  Scenario: Failed login with non-existent username
    Given I am on the login page
    When I enter username "nonexistent"
    And I enter password "password123"
    And I click the login button with username
    Then I should see an error message "Invalid email or password"
    And I should not be logged in

  @api
  Scenario: Login with invalid OTP
    Given I am on the login page
    And I have an invalid OTP code "123" and email: "testuser@example.com"
    When I enter the invalid OTP code
    And I click "Login with Code"
    Then I should see an error message "Invalid verification code"

  @ui
  Scenario: Login form validation
    Given I am on the login page
    When I leave the username field empty
    And I try to submit the form
    Then I should see a validation error for the username field
    And the form should not be submitted

#  @api
#  Scenario: Password reset request
#    Given I am on the login page
#    And I enter my email "test@example.com"
#    And I click "Send Reset Link"
#    Then I should receive a password reset email
#    And I should see a confirmation message
