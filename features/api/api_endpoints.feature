Feature: API Endpoints
  As a developer
  I want to access the application via API endpoints
  So that I can integrate with other systems

  Background:
    Given the application is running
    And the API is accessible

  @smoke @api
  Scenario: Get prayer times via API
    Given I have a valid API token
    When I make a GET request to "/api/prayers/times"
    Then I should receive a 200 response
    And the response should contain today's prayer times
    And the response should be in JSON format

  @api
  Scenario: Complete prayer via API
    Given I have a valid API token
    And I am within the Dhuhr prayer time window
    When I make a POST request to "/api/prayers/complete" With the prayer ID and completion time
    Then I should receive a 200 response
    And the prayer should be marked as completed
    And the response should contain success message

  @api
  Scenario: Get dashboard statistics via API
    Given I have a valid API token
    And I have prayer completion history
    When I make a GET request to "/api/dashboard/stats"
    Then I should receive a 200 response
    And the response should contain completion statistics
    And the response should contain weekly and monthly data

  @api
  Scenario: API authentication with invalid token
    Given I have an invalid API token
    When I make a GET request to "/api/prayers/times"
    Then I should receive a 401 response
    And the response should contain an authentication error

  @api
  Scenario: API rate limiting
    Given I have a valid API token
    When I make 100 requests to "/api/prayers/times" within 1 minute
    Then I should be rate limited
    And I should receive a 429 response
    And the response should contain rate limit information

  @api
  Scenario: API input validation
    Given I have a valid API token
    When I make a POST request to "/api/prayers/complete" With invalid prayer ID
    Then I should receive a 400 response
    And the response should contain validation error

  @api
  Scenario: API error handling
    Given I have a valid API token
    When I make a request to a non-existent endpoint
    Then I should receive a 404 response
    And the response should contain a not found error

  @api
  Scenario: API response format consistency
    Given I have a valid API token
    When I make requests to various API endpoints
    Then all responses should follow the same format
    And all responses should include appropriate status codes
    And all responses should include error handling

  @api
  Scenario: API versioning
    Given I have a valid API token
    When I make a request to "/api/v1/prayers/times"
    Then I should receive a 200 response
    And the response should be compatible with version 1

  @api
  Scenario: API documentation accessibility
    When I make a GET request to "/api/docs"
    Then I should receive a 200 response
    And the response should contain API documentation
    And the documentation should be in a readable format
