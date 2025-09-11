/**
 * Jest setup file for frontend tests.
 *
 * This file configures the test environment and provides
 * global mocks and utilities for testing.
 */

// Mock DOM environment
global.document = {
  getElementById: jest.fn(() => ({
    style: {},
    innerHTML: '',
    value: '',
    checked: false,
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(() => false),
      toggle: jest.fn()
    },
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    click: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn()
  })),
  querySelector: jest.fn(() => null),
  querySelectorAll: jest.fn(() => []),
  createElement: jest.fn((tag) => ({
    tagName: tag.toUpperCase(),
    style: {},
    innerHTML: '',
    value: '',
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(() => false),
      toggle: jest.fn()
    },
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(() => null)
  }))
};

global.window = {
  location: {
    href: 'http://localhost:5001',
    pathname: '/',
    search: '',
    hash: ''
  },
  localStorage: {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
  },
  sessionStorage: {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
  },
  alert: jest.fn(),
  confirm: jest.fn(),
  prompt: jest.fn(),
  fetch: jest.fn()
};

// Mock fetch API
global.fetch = jest.fn();

// Mock console methods to avoid noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Mock Date.now() for consistent testing
const mockDate = new Date('2024-01-15T12:00:00Z');
global.Date.now = jest.fn(() => mockDate.getTime());

// Mock setTimeout and setInterval
global.setTimeout = jest.fn((fn) => fn());
global.setInterval = jest.fn((fn) => fn());
global.clearTimeout = jest.fn();
global.clearInterval = jest.fn();

// Mock navigator.geolocation
global.navigator = {
  geolocation: {
    getCurrentPosition: jest.fn((success) => {
      success({
        coords: {
          latitude: 12.9716,
          longitude: 77.5946,
          accuracy: 10
        }
      });
    }),
    watchPosition: jest.fn(),
    clearWatch: jest.fn()
  }
};

// Mock Intl.DateTimeFormat
global.Intl = {
  DateTimeFormat: jest.fn(() => ({
    resolvedOptions: () => ({ timeZone: 'Asia/Kolkata' })
  }))
};

// Setup test utilities
global.testUtils = {
  createMockElement: (tag = 'div') => ({
    tagName: tag.toUpperCase(),
    style: {},
    innerHTML: '',
    value: '',
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(() => false),
      toggle: jest.fn()
    },
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(() => null)
  }),

  createMockUser: () => ({
    id: 1,
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    location_lat: 12.9716,
    location_lng: 77.5946,
    timezone: 'Asia/Kolkata',
    created_at: '2024-01-01T00:00:00Z'
  }),

  createMockPrayer: () => ({
    id: 1,
    name: 'Fajr',
    time: '05:30',
    completed: false,
    can_complete: true,
    is_missed: false,
    can_mark_qada: false,
    completion: null
  }),

  createMockAPIResponse: (data, success = true) => ({
    success,
    data,
    message: success ? 'Success' : 'Error',
    timestamp: new Date().toISOString()
  })
};

// Global test helpers
global.expectAsync = (promise) => {
  return expect(promise).resolves;
};

global.expectAsyncError = (promise) => {
  return expect(promise).rejects;
};

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  global.fetch.mockClear();
  global.window.localStorage.clear();
  global.window.sessionStorage.clear();
});

// Global error handler for unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
