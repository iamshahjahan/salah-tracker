Feature: Simple Authentication Test
  As a developer
  I want to test basic authentication functionality
  So that I can verify the BDD setup works

  @smoke
  Scenario: Test basic authentication setup
    Given the application is running
    And the database is clean
    When I check if authentication is available
    Then I should see that authentication is working
