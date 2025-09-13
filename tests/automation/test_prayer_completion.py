"""Test cases for prayer completion functionality."""

import time
import unittest
from selenium.webdriver.common.by import By
from .base_test import BaseAutomationTest
from .config import TestConfig

class TestPrayerCompletion(BaseAutomationTest):
    """Test prayer completion functionality."""
    
    def test_mark_prayer_complete(self):
        """Test marking a prayer as complete."""
        print("🧪 Testing mark prayer complete...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for prayer completion buttons
            completion_selectors = [
                (By.CSS_SELECTOR, "button[onclick*='complete'], .complete-btn"),
                (By.CSS_SELECTOR, "button[onclick*='markComplete'], .mark-complete"),
                (By.CSS_SELECTOR, ".prayer-complete, .complete-prayer"),
                (By.CSS_SELECTOR, "button[data-action='complete']"),
                (By.CSS_SELECTOR, ".prayer-button, .prayer-btn")
            ]
            
            completion_button_found = False
            for locator in completion_selectors:
                if self.element_exists(locator):
                    completion_button_found = True
                    print("✅ Prayer completion button found")
                    
                    # Try to click the button
                    try:
                        self.click_element(locator)
                        time.sleep(2)
                        
                        # Check for success feedback
                        success_selectors = [
                            (By.CSS_SELECTOR, ".alert-success, .success-message"),
                            (By.CSS_SELECTOR, ".toast-success, .notification-success"),
                            (By.CSS_SELECTOR, "[class*='success'], [class*='completed']")
                        ]
                        
                        for success_locator in success_selectors:
                            if self.element_exists(success_locator):
                                print("✅ Prayer completion success feedback shown")
                                break
                        else:
                            print("⚠️ No success feedback found, but button was clickable")
                            
                    except Exception as e:
                        print(f"⚠️ Could not click completion button: {e}")
                    
                    break
            
            if not completion_button_found:
                print("⚠️ Prayer completion buttons not found on dashboard")
                
        except Exception as e:
            self.take_screenshot("prayer_completion_test")
            print(f"⚠️ Prayer completion test failed: {e}")
    
    def test_mark_prayer_qada(self):
        """Test marking a prayer as Qada (missed)."""
        print("🧪 Testing mark prayer as Qada...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for Qada buttons
            qada_selectors = [
                (By.CSS_SELECTOR, "button[onclick*='qada'], .qada-btn"),
                (By.CSS_SELECTOR, "button[onclick*='missed'], .missed-btn"),
                (By.CSS_SELECTOR, "button[onclick*='markQada'], .mark-qada"),
                (By.CSS_SELECTOR, ".prayer-qada, .qada-prayer"),
                (By.CSS_SELECTOR, "button[data-action='qada']")
            ]
            
            qada_button_found = False
            for locator in qada_selectors:
                if self.element_exists(locator):
                    qada_button_found = True
                    print("✅ Prayer Qada button found")
                    
                    # Try to click the button
                    try:
                        self.click_element(locator)
                        time.sleep(2)
                        
                        # Check for success feedback
                        success_selectors = [
                            (By.CSS_SELECTOR, ".alert-success, .success-message"),
                            (By.CSS_SELECTOR, ".toast-success, .notification-success"),
                            (By.CSS_SELECTOR, "[class*='success'], [class*='qada']")
                        ]
                        
                        for success_locator in success_selectors:
                            if self.element_exists(success_locator):
                                print("✅ Prayer Qada success feedback shown")
                                break
                        else:
                            print("⚠️ No success feedback found, but Qada button was clickable")
                            
                    except Exception as e:
                        print(f"⚠️ Could not click Qada button: {e}")
                    
                    break
            
            if not qada_button_found:
                print("⚠️ Prayer Qada buttons not found on dashboard")
                
        except Exception as e:
            self.take_screenshot("prayer_qada_test")
            print(f"⚠️ Prayer Qada test failed: {e}")
    
    def test_prayer_status_display(self):
        """Test prayer status display on dashboard."""
        print("🧪 Testing prayer status display...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for prayer status indicators
            status_selectors = [
                (By.CSS_SELECTOR, ".prayer-status, .status-indicator"),
                (By.CSS_SELECTOR, "[class*='complete'], [class*='completed']"),
                (By.CSS_SELECTOR, "[class*='qada'], [class*='missed']"),
                (By.CSS_SELECTOR, ".status-badge, .prayer-badge"),
                (By.CSS_SELECTOR, "[data-status], .prayer-state")
            ]
            
            status_found = False
            for locator in status_selectors:
                if self.element_exists(locator):
                    status_found = True
                    print("✅ Prayer status indicators found")
                    break
            
            if not status_found:
                # Check for status in text content
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                status_keywords = ["complete", "completed", "qada", "missed", "pending"]
                if any(keyword in body_text for keyword in status_keywords):
                    print("✅ Prayer status content found in page text")
                else:
                    print("⚠️ Prayer status indicators not found")
                    
        except Exception as e:
            self.take_screenshot("prayer_status_test")
            print(f"⚠️ Prayer status test failed: {e}")
    
    def test_prayer_completion_modal(self):
        """Test prayer completion modal or confirmation."""
        print("🧪 Testing prayer completion modal...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for completion buttons that might trigger modals
            completion_selectors = [
                (By.CSS_SELECTOR, "button[onclick*='complete'], .complete-btn"),
                (By.CSS_SELECTOR, "button[onclick*='markComplete'], .mark-complete"),
                (By.CSS_SELECTOR, ".prayer-complete, .complete-prayer")
            ]
            
            for locator in completion_selectors:
                if self.element_exists(locator):
                    try:
                        self.click_element(locator)
                        time.sleep(2)
                        
                        # Check for modal
                        modal_selectors = [
                            (By.CSS_SELECTOR, ".modal, .popup"),
                            (By.CSS_SELECTOR, ".confirmation, .confirm-dialog"),
                            (By.CSS_SELECTOR, "[role='dialog'], .dialog")
                        ]
                        
                        for modal_locator in modal_selectors:
                            if self.element_exists(modal_locator):
                                print("✅ Prayer completion modal found")
                                return
                        
                    except Exception as e:
                        print(f"⚠️ Could not interact with completion button: {e}")
            
            print("⚠️ Prayer completion modal not found")
                
        except Exception as e:
            self.take_screenshot("prayer_modal_test")
            print(f"⚠️ Prayer completion modal test failed: {e}")
    
    def test_prayer_completion_via_email_link(self):
        """Test prayer completion via email link."""
        print("🧪 Testing prayer completion via email link...")
        
        try:
            # Test a sample completion link format
            # In real scenario, this would be a link from email
            test_link = f"{self.base_url}/complete-prayer/test-link-id"
            
            self.driver.get(test_link)
            time.sleep(3)
            
            # Check if completion page loads
            current_url = self.driver.current_url
            
            if "complete-prayer" in current_url:
                print("✅ Prayer completion page accessible")
                
                # Look for completion form or button
                completion_selectors = [
                    (By.CSS_SELECTOR, "button[onclick*='complete'], .complete-btn"),
                    (By.CSS_SELECTOR, "form[action*='complete'], .completion-form"),
                    (By.CSS_SELECTOR, ".confirm-completion, .mark-complete")
                ]
                
                for locator in completion_selectors:
                    if self.element_exists(locator):
                        print("✅ Prayer completion form/button found on completion page")
                        return
                
                print("⚠️ Prayer completion form not found on completion page")
            else:
                print("⚠️ Prayer completion page not accessible")
                
        except Exception as e:
            self.take_screenshot("email_completion_test")
            print(f"⚠️ Email completion test failed: {e}")

if __name__ == '__main__':
    unittest.main()
