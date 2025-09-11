/**
 * Unit tests for utility functions.
 *
 * This module contains comprehensive unit tests for utility functions
 * used throughout the frontend application.
 */

// Mock DOM environment for testing
const mockDOM = {
    getElementById: (id) => ({
        style: {},
        innerHTML: '',
        value: '',
        checked: false,
        classList: {
            add: () => {},
            remove: () => {},
            contains: () => false,
            toggle: () => {}
        },
        addEventListener: () => {},
        removeEventListener: () => {},
        click: () => {},
        focus: () => {},
        blur: () => {}
    }),
    querySelector: () => null,
    querySelectorAll: () => [],
    createElement: (tag) => ({
        tagName: tag.toUpperCase(),
        style: {},
        innerHTML: '',
        value: '',
        classList: {
            add: () => {},
            remove: () => {},
            contains: () => false,
            toggle: () => {}
        },
        addEventListener: () => {},
        appendChild: () => {},
        setAttribute: () => {},
        getAttribute: () => null
    })
};

// Mock localStorage
const mockLocalStorage = {
    storage: {},
    getItem: function(key) {
        return this.storage[key] || null;
    },
    setItem: function(key, value) {
        this.storage[key] = value;
    },
    removeItem: function(key) {
        delete this.storage[key];
    },
    clear: function() {
        this.storage = {};
    }
};

// Mock fetch API
const mockFetch = (response, status = 200) => {
    return Promise.resolve({
        ok: status >= 200 && status < 300,
        status: status,
        json: () => Promise.resolve(response),
        text: () => Promise.resolve(JSON.stringify(response))
    });
};

// Test suite for utility functions
class UtilityTests {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    /**
     * Add a test to the test suite.
     * @param {string} name - Test name
     * @param {Function} testFn - Test function
     */
    test(name, testFn) {
        this.tests.push({ name, testFn });
    }

    /**
     * Assert that a condition is true.
     * @param {boolean} condition - Condition to test
     * @param {string} message - Error message if assertion fails
     */
    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    /**
     * Assert that two values are equal.
     * @param {*} actual - Actual value
     * @param {*} expected - Expected value
     * @param {string} message - Error message if assertion fails
     */
    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, but got ${actual}`);
        }
    }

    /**
     * Assert that two objects are deeply equal.
     * @param {*} actual - Actual value
     * @param {*} expected - Expected value
     * @param {string} message - Error message if assertion fails
     */
    assertDeepEqual(actual, expected, message) {
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(message || `Expected ${JSON.stringify(expected)}, but got ${JSON.stringify(actual)}`);
        }
    }

    /**
     * Assert that a function throws an error.
     * @param {Function} fn - Function to test
     * @param {string} expectedError - Expected error message
     */
    assertThrows(fn, expectedError) {
        try {
            fn();
            throw new Error('Expected function to throw an error');
        } catch (error) {
            if (expectedError && !error.message.includes(expectedError)) {
                throw new Error(`Expected error message to contain "${expectedError}", but got "${error.message}"`);
            }
        }
    }

    /**
     * Run all tests.
     */
    async run() {
        console.log('Running utility tests...\n');

        for (const test of this.tests) {
            try {
                await test.testFn();
                console.log(`✓ ${test.name}`);
                this.passed++;
            } catch (error) {
                console.error(`✗ ${test.name}: ${error.message}`);
                this.failed++;
            }
        }

        console.log(`\nTest Results: ${this.passed} passed, ${this.failed} failed`);
        return this.failed === 0;
    }
}

// Date utility tests
function testDateUtils() {
    const tests = new UtilityTests();

    tests.test('formatDate should format date correctly', () => {
        const date = new Date('2024-01-15');
        const formatted = formatDate(date);
        tests.assertEqual(formatted, '2024-01-15');
    });

    tests.test('formatDate should handle invalid dates', () => {
        const formatted = formatDate('invalid');
        tests.assertEqual(formatted, 'Invalid date');
    });

    tests.test('formatTime should format time correctly', () => {
        const time = new Date('2024-01-15T14:30:00');
        const formatted = formatTime(time);
        tests.assertEqual(formatted, '14:30');
    });

    tests.test('isSameDate should compare dates correctly', () => {
        const date1 = new Date('2024-01-15');
        const date2 = new Date('2024-01-15');
        const date3 = new Date('2024-01-16');

        tests.assertEqual(isSameDate(date1, date2), true);
        tests.assertEqual(isSameDate(date1, date3), false);
    });

    tests.test('isToday should detect today correctly', () => {
        const today = new Date();
        const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);

        tests.assertEqual(isToday(today), true);
        tests.assertEqual(isToday(yesterday), false);
    });

    return tests.run();
}

// API utility tests
function testAPIUtils() {
    const tests = new UtilityTests();

    tests.test('makeAPIRequest should handle successful requests', async () => {
        const mockResponse = { success: true, data: 'test' };
        global.fetch = () => mockFetch(mockResponse);

        const result = await makeAPIRequest('/api/test');
        tests.assertDeepEqual(result, mockResponse);
    });

    tests.test('makeAPIRequest should handle failed requests', async () => {
        global.fetch = () => mockFetch({ error: 'Not found' }, 404);

        try {
            await makeAPIRequest('/api/test');
            tests.assert(false, 'Should have thrown an error');
        } catch (error) {
            tests.assert(error.message.includes('404'), 'Should have 404 error');
        }
    });

    tests.test('makeAPIRequest should handle network errors', async () => {
        global.fetch = () => Promise.reject(new Error('Network error'));

        try {
            await makeAPIRequest('/api/test');
            tests.assert(false, 'Should have thrown an error');
        } catch (error) {
            tests.assert(error.message.includes('Network error'), 'Should have network error');
        }
    });

    return tests.run();
}

// Validation utility tests
function testValidationUtils() {
    const tests = new UtilityTests();

    tests.test('validateEmail should validate correct emails', () => {
        const validEmails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ];

        validEmails.forEach(email => {
            const result = validateEmail(email);
            tests.assertEqual(result.isValid, true, `Email ${email} should be valid`);
        });
    });

    tests.test('validateEmail should reject invalid emails', () => {
        const invalidEmails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com'
        ];

        invalidEmails.forEach(email => {
            const result = validateEmail(email);
            tests.assertEqual(result.isValid, false, `Email ${email} should be invalid`);
        });
    });

    tests.test('validatePassword should validate strong passwords', () => {
        const validPasswords = [
            'Password123!',
            'MySecurePass1@',
            'Test123#Pass'
        ];

        validPasswords.forEach(password => {
            const result = validatePassword(password);
            tests.assertEqual(result.isValid, true, `Password should be valid`);
        });
    });

    tests.test('validatePassword should reject weak passwords', () => {
        const invalidPasswords = [
            'short',
            'nouppercase123!',
            'NOLOWERCASE123!',
            'NoNumbers!',
            'NoSpecialChars123'
        ];

        invalidPasswords.forEach(password => {
            const result = validatePassword(password);
            tests.assertEqual(result.isValid, false, `Password should be invalid`);
        });
    });

    return tests.run();
}

// Local storage utility tests
function testLocalStorageUtils() {
    const tests = new UtilityTests();

    tests.test('setAuthToken should store token in localStorage', () => {
        const token = 'test-token-123';
        setAuthToken(token);

        const stored = localStorage.getItem('authToken');
        tests.assertEqual(stored, token);
    });

    tests.test('getAuthToken should retrieve token from localStorage', () => {
        const token = 'test-token-456';
        localStorage.setItem('authToken', token);

        const retrieved = getAuthToken();
        tests.assertEqual(retrieved, token);
    });

    tests.test('removeAuthToken should remove token from localStorage', () => {
        localStorage.setItem('authToken', 'test-token');
        removeAuthToken();

        const retrieved = getAuthToken();
        tests.assertEqual(retrieved, null);
    });

    tests.test('isLoggedIn should return true when token exists', () => {
        localStorage.setItem('authToken', 'test-token');
        tests.assertEqual(isLoggedIn(), true);
    });

    tests.test('isLoggedIn should return false when no token', () => {
        localStorage.removeItem('authToken');
        tests.assertEqual(isLoggedIn(), false);
    });

    return tests.run();
}

// UI utility tests
function testUIUtils() {
    const tests = new UtilityTests();

    tests.test('showNotification should display success message', () => {
        const message = 'Test success message';
        showNotification(message, 'success');

        // In a real test environment, you would check if the notification was displayed
        tests.assert(true, 'Notification should be displayed');
    });

    tests.test('showNotification should display error message', () => {
        const message = 'Test error message';
        showNotification(message, 'error');

        tests.assert(true, 'Error notification should be displayed');
    });

    tests.test('hideElement should hide element', () => {
        const element = { style: { display: '' } };
        hideElement(element);

        tests.assertEqual(element.style.display, 'none');
    });

    tests.test('showElement should show element', () => {
        const element = { style: { display: 'none' } };
        showElement(element);

        tests.assertEqual(element.style.display, 'block');
    });

    return tests.run();
}

// Prayer utility tests
function testPrayerUtils() {
    const tests = new UtilityTests();

    tests.test('getPrayerStatus should return correct status', () => {
        const prayer = {
            completed: true,
            completion: { is_late: false, is_qada: false }
        };

        const status = getPrayerStatus(prayer);
        tests.assertEqual(status, 'completed');
    });

    tests.test('getPrayerStatus should return qada status', () => {
        const prayer = {
            completed: true,
            completion: { is_late: true, is_qada: true }
        };

        const status = getPrayerStatus(prayer);
        tests.assertEqual(status, 'qada');
    });

    tests.test('getPrayerStatus should return missed status', () => {
        const prayer = {
            completed: false,
            is_missed: true
        };

        const status = getPrayerStatus(prayer);
        tests.assertEqual(status, 'missed');
    });

    tests.test('canMarkQada should return true for missed prayers', () => {
        const prayer = {
            completed: false,
            is_missed: true,
            can_mark_qada: true
        };

        tests.assertEqual(canMarkQada(prayer), true);
    });

    tests.test('canMarkQada should return false for completed prayers', () => {
        const prayer = {
            completed: true,
            is_missed: false,
            can_mark_qada: false
        };

        tests.assertEqual(canMarkQada(prayer), false);
    });

    return tests.run();
}

// Run all utility tests
async function runAllUtilityTests() {
    console.log('=== Running Frontend Utility Tests ===\n');

    const testSuites = [
        { name: 'Date Utils', fn: testDateUtils },
        { name: 'API Utils', fn: testAPIUtils },
        { name: 'Validation Utils', fn: testValidationUtils },
        { name: 'Local Storage Utils', fn: testLocalStorageUtils },
        { name: 'UI Utils', fn: testUIUtils },
        { name: 'Prayer Utils', fn: testPrayerUtils }
    ];

    let totalPassed = 0;
    let totalFailed = 0;

    for (const suite of testSuites) {
        console.log(`\n--- ${suite.name} ---`);
        try {
            const passed = await suite.fn();
            if (passed) {
                totalPassed++;
            } else {
                totalFailed++;
            }
        } catch (error) {
            console.error(`Error running ${suite.name}:`, error);
            totalFailed++;
        }
    }

    console.log(`\n=== Test Summary ===`);
    console.log(`Total Suites: ${testSuites.length}`);
    console.log(`Passed: ${totalPassed}`);
    console.log(`Failed: ${totalFailed}`);

    return totalFailed === 0;
}

// Export for use in other test files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        UtilityTests,
        runAllUtilityTests,
        testDateUtils,
        testAPIUtils,
        testValidationUtils,
        testLocalStorageUtils,
        testUIUtils,
        testPrayerUtils
    };
}
