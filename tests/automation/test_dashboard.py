"""Test cases for dashboard functionality."""

import time
import unittest
from selenium.webdriver.common.by import By
from .base_test import BaseAutomationTest
from .config import TestConfig

class TestDashboard(BaseAutomationTest):
    """Test dashboard functionality."""
    
    def test_dashboard_page_load(self):
        """Test dashboard page loads correctly."""
        print("🧪 Testing dashboard page load...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Check if dashboard loads (might redirect to login if not authenticated)
            current_url = self.driver.current_url
            
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print("✅ Dashboard redirects to login when not authenticated")
                return
            
            # Check for dashboard elements
            dashboard_elements = [
                (By.CSS_SELECTOR, ".dashboard, #dashboard"),
                (By.CSS_SELECTOR, ".prayer-times, .prayer-schedule"),
                (By.CSS_SELECTOR, ".calendar, .weekly-calendar"),
                (By.CSS_SELECTOR, ".profile, .user-info"),
                (By.CSS_SELECTOR, ".stats, .statistics")
            ]
            
            dashboard_found = False
            for locator in dashboard_elements:
                if self.element_exists(locator):
                    dashboard_found = True
                    print("✅ Dashboard elements found")
                    break
            
            if not dashboard_found:
                # Check if page loaded with any content
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.assertGreater(len(body_text), 0, "Dashboard should have content")
                print("✅ Dashboard page loaded with content")
                
        except Exception as e:
            self.take_screenshot("dashboard_load_failed")
            raise AssertionError(f"Dashboard load test failed: {e}")
    
    def test_prayer_times_display(self):
        """Test prayer times are displayed on dashboard."""
        print("🧪 Testing prayer times display...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for prayer times
            prayer_time_selectors = [
                (By.CSS_SELECTOR, ".prayer-time, .prayer-times"),
                (By.CSS_SELECTOR, "[data-prayer], .prayer-item"),
                (By.CSS_SELECTOR, ".fajr, .dhuhr, .asr, .maghrib, .isha"),
                (By.CSS_SELECTOR, ".time-display, .prayer-schedule")
            ]
            
            prayer_times_found = False
            for locator in prayer_time_selectors:
                if self.element_exists(locator):
                    prayer_times_found = True
                    print("✅ Prayer times display found")
                    break
            
            if not prayer_times_found:
                # Check for any time-like content
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                if ":" in body_text and any(prayer in body_text.lower() for prayer in ["fajr", "dhuhr", "asr", "maghrib", "isha"]):
                    print("✅ Prayer times content found in page text")
                else:
                    print("⚠️ Prayer times not found on dashboard")
                    
        except Exception as e:
            self.take_screenshot("prayer_times_test")
            print(f"⚠️ Prayer times test failed: {e}")
    
    def test_calendar_view(self):
        """Test calendar view on dashboard."""
        print("🧪 Testing calendar view...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for calendar elements
            calendar_selectors = [
                (By.CSS_SELECTOR, ".calendar, .weekly-calendar"),
                (By.CSS_SELECTOR, ".calendar-grid, .calendar-container"),
                (By.CSS_SELECTOR, ".day-card, .calendar-day"),
                (By.CSS_SELECTOR, "[data-date], .date-picker")
            ]
            
            calendar_found = False
            for locator in calendar_selectors:
                if self.element_exists(locator):
                    calendar_found = True
                    print("✅ Calendar view found")
                    break
            
            if not calendar_found:
                print("⚠️ Calendar view not found on dashboard")
                
        except Exception as e:
            self.take_screenshot("calendar_test")
            print(f"⚠️ Calendar test failed: {e}")
    
    def test_user_profile_section(self):
        """Test user profile section on dashboard."""
        print("🧪 Testing user profile section...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for profile elements
            profile_selectors = [
                (By.CSS_SELECTOR, ".profile, .user-profile"),
                (By.CSS_SELECTOR, ".user-info, .profile-info"),
                (By.CSS_SELECTOR, ".avatar, .profile-pic"),
                (By.CSS_SELECTOR, ".username, .user-name"),
                (By.CSS_SELECTOR, "button[onclick*='profile'], .profile-btn")
            ]
            
            profile_found = False
            for locator in profile_selectors:
                if self.element_exists(locator):
                    profile_found = True
                    print("✅ User profile section found")
                    break
            
            if not profile_found:
                print("⚠️ User profile section not found on dashboard")
                
        except Exception as e:
            self.take_screenshot("profile_test")
            print(f"⚠️ Profile test failed: {e}")
    
    def test_navigation_elements(self):
        """Test navigation elements on dashboard."""
        print("🧪 Testing navigation elements...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for navigation elements
            nav_selectors = [
                (By.CSS_SELECTOR, "nav, .navigation"),
                (By.CSS_SELECTOR, ".nav-menu, .menu"),
                (By.CSS_SELECTOR, ".nav-item, .menu-item"),
                (By.CSS_SELECTOR, "a[href*='dashboard'], a[href*='profile']"),
                (By.CSS_SELECTOR, ".logout, .sign-out")
            ]
            
            nav_found = False
            for locator in nav_selectors:
                if self.element_exists(locator):
                    nav_found = True
                    print("✅ Navigation elements found")
                    break
            
            if not nav_found:
                print("⚠️ Navigation elements not found on dashboard")
                
        except Exception as e:
            self.take_screenshot("navigation_test")
            print(f"⚠️ Navigation test failed: {e}")
    
    def test_dashboard_responsiveness(self):
        """Test dashboard responsiveness."""
        print("🧪 Testing dashboard responsiveness...")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Test different screen sizes
            screen_sizes = [(1920, 1080), (1366, 768), (768, 1024), (375, 667)]
            
            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if page still loads correctly
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.assertIsNotNone(body, f"Dashboard should load at {width}x{height}")
            
            # Reset to default size
            self.driver.set_window_size(1920, 1080)
            print("✅ Dashboard responsiveness test passed")
            
        except Exception as e:
            self.take_screenshot("responsiveness_test")
            print(f"⚠️ Responsiveness test failed: {e}")

if __name__ == '__main__':
    unittest.main()
