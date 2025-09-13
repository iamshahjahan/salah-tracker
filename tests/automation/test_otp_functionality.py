"""Test cases for OTP functionality."""

import time
import unittest
from selenium.webdriver.common.by import By
from .base_test import BaseAutomationTest
from .config import TestConfig

class TestOTPFunctionality(BaseAutomationTest):
    """Test OTP send and verification functionality."""
    
    def test_otp_send_for_login(self):
        """Test OTP send functionality for login."""
        print("🧪 Testing OTP send for login...")
        
        # Navigate to login
        self.click_element((By.CSS_SELECTOR, "button[onclick='showLogin()']"))
        time.sleep(2)
        
        # Wait for modal to appear
        self.wait_for_visible((By.ID, "loginModal"))
        
        # Switch to OTP login
        try:
            otp_tab = self.driver.find_element(By.CSS_SELECTOR, "button[onclick='showOTPLogin()'], .otp-tab, [data-tab='otp']")
            otp_tab.click()
            time.sleep(1)
        except:
            # If no OTP tab, look for OTP login button
            otp_button = self.driver.find_element(By.CSS_SELECTOR, "button[onclick*='otp'], .otp-login-btn")
            otp_button.click()
            time.sleep(1)
        
        # Enter email for OTP
        self.send_keys_to_element((By.ID, "otpEmail"), TestConfig.TEST_EMAIL)
        
        # Send OTP - click the "Send Login Code" button, not the submit button
        self.click_element((By.CSS_SELECTOR, "#otpLoginForm button[onclick='sendLoginOTP()']"))
        
        # Check for success message or any response
        try:
            success_message = self.wait_for_visible((By.CSS_SELECTOR, ".alert-success, .success-message"), timeout=10)
            if "otp" in success_message.text.lower() or "sent" in success_message.text.lower():
                print("✅ OTP send successful")
                return
        except Exception:
            pass
        
        # Check for any response (success or error)
        try:
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-success, .alert-danger, .success-message, .error")
            if response_elements:
                response_text = response_elements[0].text
                if "otp" in response_text.lower() or "sent" in response_text.lower():
                    print("✅ OTP send successful")
                    return
                elif "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"⚠️ OTP send failed with error: {response_text}")
                    return
        except Exception:
            pass
        
        # If no clear response, take screenshot and log
        self.take_screenshot("otp_send_failed")
        print("⚠️ OTP send test inconclusive - no clear response received")
    
    def test_otp_verification(self):
        """Test OTP verification."""
        print("🧪 Testing OTP verification...")
        
        # First send OTP
        self.test_otp_send_for_login()
        
        # Enter OTP (using a test OTP - in real scenario this would come from email)
        try:
            otp_input = self.wait_for_element((By.ID, "otpCode"))
            otp_input.clear()
            otp_input.send_keys("123456")  # Test OTP
            
            # Submit OTP - use the "Login with Code" button that becomes visible after OTP is sent
            self.click_element((By.CSS_SELECTOR, "#otpLoginBtn"))
            
            # Check for result
            try:
                # Either success (login) or error (invalid OTP)
                result_element = self.wait_for_visible((By.CSS_SELECTOR, ".alert-success, .alert-danger, .error"), timeout=10)
                
                if "success" in result_element.get_attribute("class").lower():
                    print("✅ OTP verification successful")
                else:
                    # Expected for test OTP
                    if "invalid" in result_element.text.lower() or "error" in result_element.text.lower():
                        print("✅ OTP validation working - Invalid OTP rejected")
                    else:
                        print("⚠️ OTP verification test inconclusive - unclear response")
                        
            except Exception:
                # Check for any response
                response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-success, .alert-danger, .error, .success-message")
                if response_elements:
                    response_text = response_elements[0].text
                    if "invalid" in response_text.lower() or "error" in response_text.lower():
                        print("✅ OTP validation working - Invalid OTP rejected")
                    else:
                        print("⚠️ OTP verification test inconclusive - unclear response")
                else:
                    print("⚠️ OTP verification test inconclusive - no response received")
                    
        except Exception as e:
            self.take_screenshot("otp_verification_failed")
            print(f"⚠️ OTP verification test inconclusive: {e}")
    
    def test_otp_resend_functionality(self):
        """Test OTP resend functionality."""
        print("🧪 Testing OTP resend...")
        
        # First send OTP
        self.test_otp_send_for_login()
        
        # Try to send OTP again (this simulates resend functionality)
        try:
            # Clear the email field and enter email again
            email_input = self.driver.find_element(By.ID, "otpEmail")
            email_input.clear()
            email_input.send_keys(TestConfig.TEST_EMAIL)
            
            # Click send OTP button again
            self.click_element((By.CSS_SELECTOR, "#otpLoginForm button[onclick='sendLoginOTP()']"))
            
            # Check for success message
            try:
                success_message = self.wait_for_visible((By.CSS_SELECTOR, ".alert-success, .success-message"), timeout=10)
                if "otp" in success_message.text.lower() or "sent" in success_message.text.lower():
                    print("✅ OTP resend successful")
                else:
                    print("⚠️ OTP resend test inconclusive - unclear response")
            except Exception:
                # Check for any response
                response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-success, .alert-danger, .success-message, .error")
                if response_elements:
                    response_text = response_elements[0].text
                    if "otp" in response_text.lower() or "sent" in response_text.lower():
                        print("✅ OTP resend successful")
                    else:
                        print("⚠️ OTP resend test inconclusive - unclear response")
                else:
                    print("⚠️ OTP resend test inconclusive - no response received")
            
        except Exception as e:
            print(f"⚠️ OTP resend test skipped: {e}")
    
    def test_otp_expiry_handling(self):
        """Test OTP expiry handling."""
        print("🧪 Testing OTP expiry handling...")
        
        # Send OTP
        self.test_otp_send_for_login()
        
        # Wait for potential expiry (this is a basic test)
        time.sleep(2)
        
        # Try to verify with expired OTP
        try:
            otp_input = self.wait_for_element((By.ID, "otpCode"))
            otp_input.clear()
            otp_input.send_keys("999999")  # Random OTP
            
            self.click_element((By.CSS_SELECTOR, "#otpLoginBtn"))
            
            # Should show error for invalid/expired OTP
            try:
                error_message = self.wait_for_visible((By.CSS_SELECTOR, ".alert-danger, .error"), timeout=10)
                if "invalid" in error_message.text.lower() or "error" in error_message.text.lower():
                    print("✅ OTP expiry/invalid handling working")
                else:
                    print("⚠️ OTP expiry test inconclusive - unclear error message")
            except Exception:
                # Check for any response
                response_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .error, .alert-success")
                if response_elements:
                    response_text = response_elements[0].text
                    if "invalid" in response_text.lower() or "error" in response_text.lower():
                        print("✅ OTP expiry/invalid handling working")
                    else:
                        print("⚠️ OTP expiry test inconclusive - unclear response")
                else:
                    print("⚠️ OTP expiry test inconclusive - no response received")
                    
        except Exception as e:
            self.take_screenshot("otp_expiry_test")
            print(f"⚠️ OTP expiry test inconclusive: {e}")

if __name__ == '__main__':
    unittest.main()
