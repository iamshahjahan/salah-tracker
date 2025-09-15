# BDD Features Directory

This directory contains all the BDD (Behavior-Driven Development) feature files written in Gherkin syntax.

## Structure

```
features/
├── authentication/          # User authentication features
├── prayer_tracking/        # Prayer tracking and completion features
├── email_verification/     # Email verification features
├── dashboard/              # Dashboard and statistics features
├── family_management/      # Family member management features
├── notifications/          # Notification and reminder features
├── api/                    # API endpoint features
└── support/                # Supporting files (step definitions, etc.)
```

## Writing Features

Each feature file should follow the Gherkin syntax:

```gherkin
Feature: Feature Name
  As a [user type]
  I want to [goal]
  So that [benefit]

  Background:
    Given some initial context

  Scenario: Scenario name
    Given some precondition
    When some action is performed
    Then some expected result should occur
```

## Running BDD Tests

```bash
# Run all BDD tests
behave

# Run specific feature
behave features/authentication/

# Run with specific tags
behave --tags=@smoke

# Generate HTML report
behave --format=html -o reports/
```

## Tags

Use tags to categorize scenarios:
- `@smoke` - Critical functionality tests
- `@regression` - Full regression test suite
- `@api` - API-specific tests
- `@ui` - User interface tests
- `@slow` - Tests that take longer to run
