# Salah Tracker - Automation Test Suite

This directory contains end-to-end automation tests for the Salah Tracker application.

## 🎯 Test Coverage

The automation test suite covers the following critical functionality:

1. **User Registration** (`test_user_registration.py`)
   - Successful user registration
   - Form validation
   - Duplicate email handling

2. **OTP Functionality** (`test_otp_functionality.py`)
   - OTP send for login
   - OTP verification
   - OTP resend functionality
   - OTP expiry handling

3. **Reminder Functionality** (`test_reminder_functionality.py`)
   - Reminder send via API
   - Reminder settings page
   - Email reminder configuration
   - Reminder time selection
   - Reminder frequency settings

4. **Dashboard** (`test_dashboard.py`)
   - Dashboard page load
   - Prayer times display
   - Calendar view
   - User profile section
   - Navigation elements
   - Responsiveness

5. **Prayer Completion** (`test_prayer_completion.py`)
   - Mark prayer as complete
   - Mark prayer as Qada (missed)
   - Prayer status display
   - Prayer completion modal
   - Prayer completion via email link

## 🚀 Setup

### Prerequisites

1. **Python 3.8+**
2. **Chrome Browser** (for Selenium WebDriver)
3. **Internet Connection** (to access salahtracker.app)

### Installation

1. Install automation test dependencies:
```bash
pip install -r requirements-automation.txt
```

2. The Chrome WebDriver will be automatically downloaded by `webdriver-manager`.

## 🧪 Running Tests

### Run All Automation Tests

#### Sequential Execution (Default)
```bash
python3 tests/automation/run_automation_tests.py
```

#### Parallel Execution (Faster)
```bash
# Run with 3 workers (default)
python3 tests/automation/run_automation_tests.py --parallel

# Run with custom number of workers
python3 tests/automation/run_automation_tests.py --parallel --workers=5

# Using environment variable
PARALLEL_TESTS=true python3 tests/automation/run_automation_tests.py
```

#### Using the Comprehensive Test Runner
```bash
# Run all test suites (including automation) sequentially
python3 run_all_tests.py

# Run all test suites with parallel automation tests
python3 run_all_tests.py --parallel

# Run with custom worker count
python3 run_all_tests.py --parallel --workers=4
```

### Performance Comparison
- **Sequential**: ~2-3 minutes for full test suite
- **Parallel (3 workers)**: ~1-1.5 minutes for full test suite
- **Parallel (5 workers)**: ~45-60 seconds for full test suite

> **Note**: Parallel execution uses separate browser instances per thread, so it may consume more system resources but significantly reduces total execution time.

### Run Individual Test Modules
```bash
# User registration tests
python3 -m unittest tests.automation.test_user_registration

# OTP functionality tests
python3 -m unittest tests.automation.test_otp_functionality

# Reminder functionality tests
python3 -m unittest tests.automation.test_reminder_functionality

# Dashboard tests
python3 -m unittest tests.automation.test_dashboard

# Prayer completion tests
python3 -m unittest tests.automation.test_prayer_completion
```

### Run Specific Test Cases
```bash
# Run specific test method
python3 -m unittest tests.automation.test_user_registration.TestUserRegistration.test_user_registration_success
```

## ⚙️ Configuration

### Test Configuration (`config.py`)

- **BASE_URL**: Points to `https://salahtracker.app`
- **HEADLESS**: Set to `true` for headless browser mode
- **Timeouts**: Configurable wait times for elements
- **Test Credentials**: Default test user credentials

### Environment Variables

You can override default settings using environment variables:

```bash
export HEADLESS=true  # Run tests in headless mode
export BASE_URL=https://staging.salahtracker.app  # Use staging environment
```

## 📸 Screenshots

Test failures automatically capture screenshots in the `screenshots/` directory for debugging purposes.

## 🔧 Test Structure

### Base Test Class (`base_test.py`)

Provides common functionality for all test classes:
- WebDriver setup and teardown
- Element waiting and interaction methods
- Screenshot capture
- Common assertions

### Test Classes

Each test class inherits from `BaseAutomationTest` and focuses on specific functionality:
- **TestUserRegistration**: User registration flows
- **TestOTPFunctionality**: OTP send and verification
- **TestReminderFunctionality**: Reminder system testing
- **TestDashboard**: Dashboard functionality
- **TestPrayerCompletion**: Prayer completion flows

## 🚦 CI/CD Integration

### Pre-commit Hook

Automation tests are integrated into the pre-commit hook:
- Runs critical tests first
- Runs automation tests if dependencies are available
- Blocks commits if tests fail

### Pre-deployment

Run comprehensive test suite before production deployment:
```bash
python3 run_all_tests.py
```

## 🐛 Debugging

### Common Issues

1. **WebDriver Issues**
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

2. **Element Not Found**
   - Check if the application UI has changed
   - Verify selectors in test files
   - Check screenshots for visual debugging

3. **Timeout Issues**
   - Increase wait times in `config.py`
   - Check application performance
   - Verify network connectivity

### Debug Mode

Run tests with verbose output:
```bash
python3 -m unittest tests.automation.test_user_registration -v
```

## 📊 Test Reports

Tests provide detailed output including:
- Test execution status
- Screenshot capture on failures
- Timing information
- Detailed error messages

## 🔄 Maintenance

### Updating Tests

When the application UI changes:
1. Update element selectors in test files
2. Add new test cases for new functionality
3. Update test data and credentials
4. Verify tests still pass

### Adding New Tests

1. Create new test file in `tests/automation/`
2. Inherit from `BaseAutomationTest`
3. Add test methods following naming convention `test_*`
4. Update `run_automation_tests.py` to include new module

## 📝 Best Practices

1. **Use explicit waits** instead of `time.sleep()`
2. **Take screenshots** on test failures
3. **Clean up** after each test (cookies, storage)
4. **Use meaningful test names** and descriptions
5. **Handle exceptions gracefully** with proper error messages
6. **Keep tests independent** - no dependencies between tests
7. **Use page object pattern** for complex pages (future enhancement)

## 🎯 Future Enhancements

- [ ] Page Object Model implementation
- [ ] Cross-browser testing (Firefox, Safari)
- [ ] Mobile testing with Appium
- [ ] API testing integration
- [ ] Performance testing
- [ ] Visual regression testing
- [ ] Test data management
- [ ] Parallel test execution
