"""Configuration for automation tests."""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestConfig:
    """Configuration for automation tests."""
    
    # Base URL for testing
    BASE_URL = "http://localhost:5001"
    
    # Test user credentials
    TEST_EMAIL = "test.automation@localhost.com"
    TEST_PASSWORD = "TestPassword123!"
    TEST_FIRST_NAME = "Test"
    TEST_LAST_NAME = "User"
    TEST_PHONE = "+1234567890"
    
    # Timeouts
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 20
    PAGE_LOAD_TIMEOUT = 30
    
    # Browser settings
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    WINDOW_SIZE = (1920, 1080)

class WebDriverFactory:
    """Factory for creating WebDriver instances."""
    
    @staticmethod
    def create_chrome_driver():
        """Create a Chrome WebDriver instance."""
        import tempfile
        import threading
        
        options = Options()
        
        if TestConfig.HEADLESS:
            options.add_argument('--headless')
        
        # Create unique user data directory for parallel execution
        temp_dir = tempfile.mkdtemp(prefix=f"selenium_chrome_{threading.get_ident()}_")
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable JavaScript for faster loading (we'll enable it selectively)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set timeouts
        driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
        driver.set_page_load_timeout(TestConfig.PAGE_LOAD_TIMEOUT)
        
        return driver
