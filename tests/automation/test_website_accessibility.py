#!/usr/bin/env python3
"""Simple test to verify website accessibility."""

import unittest
import requests
from .config import TestConfig

class TestWebsiteAccessibility(unittest.TestCase):
    """Test basic website accessibility."""
    
    def test_website_loads(self):
        """Test that the website loads successfully."""
        print("🧪 Testing website accessibility...")
        
        try:
            response = requests.get(TestConfig.BASE_URL, timeout=10)
            self.assertEqual(response.status_code, 200, "Website should return 200 OK")
            print("✅ Website loads successfully")
            
            # Check if it's the right page
            self.assertIn("SalahTracker", response.text, "Should contain SalahTracker in content")
            print("✅ Website contains expected content")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Website not accessible: {e}")
    
    def test_website_https(self):
        """Test that website uses HTTPS."""
        print("🧪 Testing HTTPS...")
        
        try:
            response = requests.get(TestConfig.BASE_URL, timeout=10)
            self.assertTrue(response.url.startswith('https://'), "Website should use HTTPS")
            print("✅ Website uses HTTPS")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"HTTPS test failed: {e}")

if __name__ == '__main__':
    unittest.main()
