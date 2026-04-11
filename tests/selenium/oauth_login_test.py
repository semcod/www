#!/usr/bin/env python3
"""
Selenium E2E test for GitHub OAuth login simulation
Tests the complete OAuth flow using different browsers
"""

import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class OAuthLoginTest(unittest.TestCase):
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    MOCK_GITHUB_URL = os.getenv('MOCK_GITHUB_URL', 'http://localhost:4010')

    def setUp(self):
        """Set up browser before each test"""
        self.driver = None
        self.wait = None

    def tearDown(self):
        """Clean up after each test"""
        if self.driver:
            self.driver.quit()

    def setup_chrome_driver(self):
        """Set up Chrome driver with options"""
        options = ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode for CI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def setup_firefox_driver(self):
        """Set up Firefox driver with options"""
        options = FirefoxOptions()
        options.add_argument('--headless')
        
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def test_oauth_login_chrome(self):
        """Test OAuth login flow with Chrome"""
        self.setup_chrome_driver()
        self._perform_oauth_login()

    def test_oauth_login_firefox(self):
        """Test OAuth login flow with Firefox"""
        self.setup_firefox_driver()
        self._perform_oauth_login()

    def _perform_oauth_login(self):
        """Common OAuth login flow implementation"""
        # Navigate to frontend
        self.driver.get(self.FRONTEND_URL)
        
        # Wait for page to load
        self.wait.until(EC.presence_of_element_located((By.ID, "root")))
        
        # Find and click GitHub login button
        login_selectors = [
            "//button[contains(text(), 'GitHub')]",
            "//a[contains(text(), 'GitHub')]",
            "//button[contains(text(), 'Sign in')]",
            "//a[contains(text(), 'Sign in')]",
            "//*[@data-testid='github-login']"
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                if selector.startswith('//'):
                    login_button = self.driver.find_element(By.XPATH, selector)
                else:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if login_button.is_displayed():
                    break
            except:
                continue
        
        self.assertIsNotNone(login_button, "GitHub login button not found")
        login_button.click()
        
        # Wait for redirect to mock GitHub
        self.wait.until(lambda driver: self.MOCK_GITHUB_URL in driver.current_url)
        self.assertIn('4010', self.driver.current_url)
        self.assertIn('login/oauth/authorize', self.driver.current_url)
        
        # Verify we're on the mock GitHub login page
        page_text = self.driver.page_source
        self.assertIn('Mock GitHub Login', page_text)
        
        # Find and click the tom-sapletta-com user button
        user_selectors = [
            "//button[contains(text(), 'tom-sapletta-com')]",
            "//button[contains(text(), 'Tom Sapletta')]",
            "//button[contains(text(), 'tom-sapletta-com')]",
            "//button"
        ]
        
        user_button = None
        for selector in user_selectors:
            try:
                if selector.startswith('//'):
                    user_button = self.driver.find_element(By.XPATH, selector)
                else:
                    user_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if user_button.is_displayed() and 'tom-sapletta-com' in user_button.text:
                    break
            except:
                continue
        
        self.assertIsNotNone(user_button, "tom-sapletta-com user button not found")
        user_button.click()
        
        # Wait for redirect back to frontend
        self.wait.until(lambda driver: self.FRONTEND_URL in driver.current_url and 'auth/callback' not in driver.current_url)
        self.assertTrue(self.driver.current_url.startswith(self.FRONTEND_URL))
        
        # Verify user is logged in
        page_text = self.driver.page_source
        self.assertIn('tom-sapletta-com', page_text)
        
        # Take screenshot for debugging
        self.driver.save_screenshot(f'test-results/selenium-login-{self.driver.name}.png')

    def test_oauth_login_with_explicit_waits(self):
        """Test OAuth flow with explicit waits and verification"""
        self.setup_chrome_driver()
        
        # Navigate to frontend
        self.driver.get(self.FRONTEND_URL)
        
        # Explicit wait for login button
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'GitHub')] | //a[contains(text(), 'GitHub')]"))
        )
        login_button.click()
        
        # Wait for URL to contain mock GitHub URL
        self.wait.until(lambda driver: self.MOCK_GITHUB_URL in driver.current_url)
        
        # Verify mock GitHub page title
        self.assertIn('Mock GitHub Login', self.driver.page_source)
        
        # Wait for and click user button
        user_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'tom-sapletta-com')]"))
        )
        user_button.click()
        
        # Wait for redirect back to frontend
        self.wait.until(lambda driver: self.FRONTEND_URL in driver.current_url and 'auth/callback' not in driver.current_url)
        
        # Verify login success
        self.assertIn('tom-sapletta-com', self.driver.page_source)

    def test_session_persistence(self):
        """Test that login session persists across page reloads"""
        self.setup_chrome_driver()
        
        # Complete login flow
        self._perform_oauth_login()
        
        # Reload the page
        self.driver.refresh()
        
        # Wait for page to reload
        self.wait.until(EC.presence_of_element_located((By.ID, "root")))
        
        # Verify still logged in
        page_text = self.driver.page_source
        self.assertIn('tom-sapletta-com', page_text)

if __name__ == '__main__':
    # Create test results directory
    os.makedirs('test-results', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)
