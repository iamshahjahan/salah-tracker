"""Base test class for automation tests."""

import time
import unittest
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .config import TestConfig, WebDriverFactory

class BaseAutomationTest(unittest.TestCase):
    """Base class for all automation tests."""
    
    # Thread-local storage for WebDriver instances
    _local = threading.local()
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        # Each thread gets its own WebDriver instance
        cls._local.driver = WebDriverFactory.create_chrome_driver()
        cls._local.wait = WebDriverWait(cls._local.driver, TestConfig.EXPLICIT_WAIT)
        cls.base_url = TestConfig.BASE_URL
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test class."""
        if hasattr(cls._local, 'driver'):
            cls._local.driver.quit()
    
    @property
    def driver(self):
        """Get the thread-local WebDriver instance."""
        return self._local.driver
    
    @property
    def wait(self):
        """Get the thread-local WebDriverWait instance."""
        return self._local.wait
    
    def setUp(self):
        """Set up each test."""
        self.driver.get(self.base_url)
        time.sleep(2)  # Allow page to load
    
    def tearDown(self):
        """Clean up after each test."""
        # Clear any cookies or local storage
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
    
    def wait_for_element(self, locator, timeout=None):
        """Wait for an element to be present and return it."""
        if timeout is None:
            timeout = TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
    
    def wait_for_clickable(self, locator, timeout=None):
        """Wait for an element to be clickable and return it."""
        if timeout is None:
            timeout = TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))
    
    def wait_for_visible(self, locator, timeout=None):
        """Wait for an element to be visible and return it."""
        if timeout is None:
            timeout = TestConfig.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def element_exists(self, locator):
        """Check if an element exists without waiting."""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def get_element_text(self, locator):
        """Get text from an element."""
        element = self.wait_for_element(locator)
        return element.text
    
    def click_element(self, locator):
        """Click an element."""
        element = self.wait_for_clickable(locator)
        element.click()
    
    def send_keys_to_element(self, locator, text):
        """Send keys to an element."""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)
    
    def scroll_to_element(self, locator):
        """Scroll to an element."""
        element = self.wait_for_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
    
    def take_screenshot(self, name):
        """Take a screenshot for debugging."""
        timestamp = int(time.time())
        filename = f"screenshots/{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
    
    def wait_for_page_load(self):
        """Wait for page to fully load."""
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
