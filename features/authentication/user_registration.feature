Feature: User Registration
  As a new user
  I want to register for an account
  So that I can track my prayers and receive reminders

  Background:
    Given the application is running
    And the database is clean

  @smoke @api
  Scenario: Successful user registration
    Given I am on the registration page
    When I fill in the registration form with:
      | Field        | Value              |
      | username     | testuser123        |
      | email        | test@example.com   |
      | password     | securepassword123  |
      | first_name   | Test               |
      | last_name    | User               |
    And I submit the registration form
    Then I should be registered successfully
    And I should receive a confirmation message
    And I should be automatically logged in
    And an email verification should be sent to my email

  @api
  Scenario: Registration with duplicate email
    Given a user with email "existing@example.com" already exists
    When I try to register with email "existing@example.com"
    Then I should see an error message "User with this email already exists"
    And I should not be registered

  @api
  Scenario: Registration with invalid email format
    When I try to register with email "invalid-email"
    Then I should see an error message about invalid email format

  @api
  Scenario: Registration with weak password
    When I try to register with password "123"
    Then I should see an error message about password requirements
    And I should not be registered

  @api
  Scenario: Registration with missing required fields
    When I submit the registration form without filling required fields
    Then I should see error messages for missing fields
    And I should not be registered
