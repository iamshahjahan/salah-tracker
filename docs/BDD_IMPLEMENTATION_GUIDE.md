# BDD Implementation Guide for Salah Tracker

## Overview

This guide explains how to implement and use Behavior-Driven Development (BDD) in the Salah Tracker project. BDD helps ensure that the application behaves correctly from the user's perspective by writing tests in natural language.

## What is BDD?

BDD (Behavior-Driven Development) is a software development approach that:
- Focuses on the behavior of the application from the user's perspective
- Uses natural language to describe features and scenarios
- Bridges the gap between business requirements and technical implementation
- Ensures all stakeholders understand what the application should do

## BDD Structure

### 1. Features
Features are written in Gherkin syntax and describe the behavior of the application:

```gherkin
Feature: User Registration
  As a new user
  I want to register for an account
  So that I can track my prayers and receive reminders

  Scenario: Successful user registration
    Given I am on the registration page
    When I fill in the registration form with valid data
    Then I should be registered successfully
```

### 2. Step Definitions
Step definitions are Python functions that implement the steps in the feature files:

```python
@given('I am on the registration page')
def step_on_registration_page(context):
    context.current_page = 'registration'
```

### 3. Environment Setup
The environment file sets up the test environment before and after scenarios:

```python
def before_scenario(context, scenario):
    # Set up test data
    pass

def after_scenario(context, scenario):
    # Clean up test data
    pass
```

## Project Structure

```
features/
├── authentication/          # User authentication features
│   ├── user_registration.feature
│   └── user_login.feature
├── email_verification/     # Email verification features
│   └── email_verification.feature
├── prayer_tracking/        # Prayer tracking features
│   └── prayer_completion.feature
├── dashboard/              # Dashboard features
│   └── dashboard_statistics.feature
└── support/                # Supporting files
    ├── environment.py      # Test environment setup
    └── steps/              # Step definitions
        ├── authentication_steps.py
        ├── email_verification_steps.py
        └── prayer_completion_steps.py
```

## Writing Features

### Feature Template

```gherkin
Feature: [Feature Name]
  As a [user type]
  I want to [goal]
  So that [benefit]

  Background:
    Given some initial context

  @tag1 @tag2
  Scenario: [Scenario name]
    Given some precondition
    When some action is performed
    Then some expected result should occur
```

### Example Feature

```gherkin
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
```

## Writing Step Definitions

### Step Definition Template

```python
from behave import given, when, then

@given('some precondition')
def step_precondition(context):
    # Set up the precondition
    pass

@when('some action is performed')
def step_action(context):
    # Perform the action
    pass

@then('some expected result should occur')
def step_result(context):
    # Verify the result
    assert some_condition
```

### Example Step Definition

```python
@given('I am logged in as a user')
def step_logged_in_as_user(context):
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    context.current_user = user
    context.is_logged_in = True
```

## Tags

Use tags to categorize and organize scenarios:

- `@smoke` - Critical functionality tests
- `@regression` - Full regression test suite
- `@api` - API-specific tests
- `@ui` - User interface tests
- `@slow` - Tests that take longer to run
- `@skip` - Tests to skip

## Running BDD Tests

### Install Dependencies

```bash
pip install -r config/requirements-bdd.txt
```

### Run All Tests

```bash
python tools/run_bdd_tests.py
```

### Run Specific Tags

```bash
# Run smoke tests only
python tools/run_bdd_tests.py --smoke

# Run API tests only
python tools/run_bdd_tests.py --api

# Run specific tags
python tools/run_bdd_tests.py --tags @smoke,@api
```

### Run Specific Feature

```bash
python tools/run_bdd_tests.py --feature features/authentication/
```

### Generate Reports

```bash
python tools/run_bdd_tests.py --format html --report
```

## Best Practices

### 1. Feature Writing
- Write features from the user's perspective
- Use clear, descriptive language
- Keep scenarios focused and atomic
- Use Background for common setup
- Use tags to organize scenarios

### 2. Step Definitions
- Keep steps reusable across scenarios
- Use context to share data between steps
- Implement proper error handling
- Clean up test data after scenarios

### 3. Test Data Management
- Use factories for creating test data
- Clean up data between scenarios
- Use realistic test data
- Avoid hardcoded values

### 4. Environment Setup
- Set up test environment properly
- Clean up after each scenario
- Use in-memory database for tests
- Mock external services

## Integration with CI/CD

### Pre-commit Hook

Add BDD tests to your pre-commit hook:

```bash
#!/bin/bash
echo "Running BDD smoke tests..."
python tools/run_bdd_tests.py --smoke
if [ $? -ne 0 ]; then
    echo "BDD tests failed!"
    exit 1
fi
```

### GitHub Actions

```yaml
name: BDD Tests
on: [push, pull_request]
jobs:
  bdd-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r config/requirements-bdd.txt
      - name: Run BDD tests
        run: python tools/run_bdd_tests.py --smoke
```

## Troubleshooting

### Common Issues

1. **Step Definition Not Found**
   - Check that step definition file is in the correct directory
   - Ensure the step text matches exactly
   - Check for typos in step definitions

2. **Database Issues**
   - Ensure test database is properly set up
   - Check that data is cleaned up between scenarios
   - Verify database connections

3. **Context Issues**
   - Ensure context variables are properly initialized
   - Check that data is shared correctly between steps
   - Verify context cleanup

### Debug Mode

Run tests in debug mode to see more details:

```bash
behave --logging-level=DEBUG
```

## Benefits of BDD

1. **Clear Requirements**: Features serve as living documentation
2. **Better Communication**: Business and technical teams speak the same language
3. **Quality Assurance**: Tests ensure the application works as expected
4. **Regression Prevention**: Automated tests catch breaking changes
5. **User Focus**: Tests are written from the user's perspective

## Next Steps

1. Write more feature files for existing functionality
2. Implement step definitions for all scenarios
3. Add UI tests using Selenium
4. Integrate with CI/CD pipeline
5. Generate comprehensive test reports
6. Add performance testing scenarios

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
