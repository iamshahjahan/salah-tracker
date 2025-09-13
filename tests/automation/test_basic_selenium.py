#!/usr/bin/env python3
"""Basic Selenium test to verify browser automation works."""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from selenium.webdriver.common.by import By
from .base_test import BaseAutomationTest
from .config import TestConfig

class TestBasicSelenium(BaseAutomationTest):
    """Basic Selenium functionality test."""
    
    def test_website_loads_in_browser(self):
        """Test that website loads in browser."""
        print("🧪 Testing website loads in browser...")
        
        # Navigate to website
        self.driver.get(TestConfig.BASE_URL)
        time.sleep(3)
        
        # Check page title
        title = self.driver.title
        self.assertIn("SalahTracker", title, "Page title should contain SalahTracker")
        print(f"✅ Page title: {title}")
        
        # Check for main content
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body, "Body element should exist")
        print("✅ Page body loaded")
        
        # Check for navigation
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar, .navigation")
        self.assertGreater(len(nav_elements), 0, "Should have navigation elements")
        print("✅ Navigation elements found")
        
        # Check for main content sections
        main_content = self.driver.find_elements(By.CSS_SELECTOR, "main, .main-content, #app")
        self.assertGreater(len(main_content), 0, "Should have main content")
        print("✅ Main content found")
    
    def test_login_button_exists(self):
        """Test that login button exists."""
        print("🧪 Testing login button exists...")
        
        # Navigate to website
        self.driver.get(TestConfig.BASE_URL)
        time.sleep(3)
        
        # Look for login buttons
        login_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick='showLogin()']")
        
        if len(login_buttons) == 0:
            # Try alternative selectors
            login_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn[onclick*='login']")
        
        if len(login_buttons) == 0:
            # Look for buttons with specific text
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            login_buttons = [btn for btn in all_buttons if 'login' in btn.text.lower() or 'get started' in btn.text.lower()]
        
        if len(login_buttons) == 0:
            # Check all buttons
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(all_buttons)} buttons on page")
            for i, btn in enumerate(all_buttons[:5]):  # Show first 5 buttons
                print(f"Button {i+1}: {btn.text} - onclick: {btn.get_attribute('onclick')}")
        
        self.assertGreater(len(login_buttons), 0, "Should have login button")
        print("✅ Login button found")
    
    def test_register_button_exists(self):
        """Test that register button exists."""
        print("🧪 Testing register button exists...")
        
        # Navigate to website
        self.driver.get(TestConfig.BASE_URL)
        time.sleep(3)
        
        # Look for register buttons
        register_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[onclick='showRegister()']")
        
        if len(register_buttons) == 0:
            # Try alternative selectors
            register_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn[onclick*='register']")
        
        if len(register_buttons) == 0:
            # Look for buttons with specific text
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            register_buttons = [btn for btn in all_buttons if 'register' in btn.text.lower() or 'create account' in btn.text.lower()]
        
        if len(register_buttons) == 0:
            # Check all buttons
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(all_buttons)} buttons on page")
            for i, btn in enumerate(all_buttons[:5]):  # Show first 5 buttons
                print(f"Button {i+1}: {btn.text} - onclick: {btn.get_attribute('onclick')}")
        
        self.assertGreater(len(register_buttons), 0, "Should have register button")
        print("✅ Register button found")

if __name__ == '__main__':
    unittest.main()
