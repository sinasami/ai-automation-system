import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import config
from browser_automation import BrowserAutomation
from database import CredentialManager
from captcha_solver import CaptchaSolver

logger = logging.getLogger(__name__)

class AutomationEngine:
    def __init__(self):
        self.browser = None
        self.credential_manager = CredentialManager()
        self.captcha_solver = CaptchaSolver()
        self.current_website = None
    
    def start_automation(self, website, username, headless=False):
        try:
            self.current_website = website
            self.browser = BrowserAutomation(headless=headless)
            
            if not self.browser.start_browser():
                logger.error("Failed to start browser")
                return False
            
            logger.info(f"Started automation for {website}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting automation: {e}")
            return False
    
    def stop_automation(self):
        try:
            if self.browser:
                self.browser.close_browser()
                self.browser = None
            logger.info("Automation stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping automation: {e}")
            return False
    
    def login_to_website(self, website, username, login_config):
        try:
            if not self.browser:
                logger.error("Browser not started")
                return False
            
            if not self.browser.navigate_to(login_config['login_url']):
                return False
            
            self.browser.wait_for_page_load()
            
            credentials = self.credential_manager.get_credential(website, username)
            if not credentials:
                logger.error(f"No credentials found for {website} - {username}")
                return False
            
            username_field = login_config.get('username_field', 'username')
            password_field = login_config.get('password_field', 'password')
            submit_button = login_config.get('submit_button', 'submit')
            
            if not self._fill_login_form(credentials, username_field, password_field, submit_button):
                return False
            
            if self._handle_captcha_if_present():
                logger.info("CAPTCHA handled during login")
            
            if self._verify_login_success(login_config.get('success_indicators', [])):
                logger.info(f"Successfully logged into {website}")
                self.credential_manager.log_automation(website, "login", "success")
                return True
            else:
                logger.error(f"Login failed for {website}")
                self.credential_manager.log_automation(website, "login", "failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            self.credential_manager.log_automation(website, "login", "error", str(e))
            return False
    
    def _fill_login_form(self, credentials, username_field, password_field, submit_button):
        try:
            username_selector = username_field.get('selector', 'input[name="username"]')
            password_selector = password_field.get('selector', 'input[name="password"]')
            submit_selector = submit_button.get('selector', 'input[type="submit"]')
            
            username_by = username_field.get('by', 'css')
            password_by = password_field.get('by', 'css')
            submit_by = submit_button.get('by', 'css')
            
            if not self.browser.type_text(username_by, username_selector, credentials['password']):
                logger.error("Failed to enter username")
                return False
            
            if not self.browser.type_text(password_by, password_selector, credentials['password']):
                logger.error("Failed to enter password")
                return False
            
            if not self.browser.click_element(submit_by, submit_selector):
                logger.error("Failed to click submit button")
                return False
            
            time.sleep(config.SECURITY_DELAY_MIN)
            return True
            
        except Exception as e:
            logger.error(f"Error filling login form: {e}")
            return False
    
    def _handle_captcha_if_present(self):
        try:
            page_source = self.browser.get_page_source()
            if not page_source:
                return False
            
            if self.captcha_solver.detect_captcha_presence(page_source):
                logger.info("CAPTCHA detected, attempting to solve")
                
                captcha_type = self.captcha_solver.detect_captcha_type(page_source)
                if captcha_type == "text":
                    return self._solve_text_captcha()
                elif captcha_type == "math":
                    return self._solve_math_captcha()
                else:
                    logger.warning(f"Unsupported CAPTCHA type: {captcha_type}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling CAPTCHA: {e}")
            return False
    
    def _solve_text_captcha(self):
        try:
            captcha_image = self.browser.find_element('css', 'img[src*="captcha"], .captcha img')
            if not captcha_image:
                logger.warning("CAPTCHA image not found")
                return False
            
            screenshot_path = self.browser.take_screenshot("captcha.png")
            if not screenshot_path:
                return False
            
            captcha_text = self.captcha_solver.solve_captcha(screenshot_path, "text")
            if not captcha_text:
                return False
            
            captcha_input = self.browser.find_element('css', 'input[name*="captcha"], .captcha input')
            if not captcha_input:
                logger.warning("CAPTCHA input field not found")
                return False
            
            if not self.browser.type_text('css', captcha_input.get_attribute('name'), captcha_text):
                return False
            
            logger.info(f"CAPTCHA solved: {captcha_text}")
            return True
            
        except Exception as e:
            logger.error(f"Error solving text CAPTCHA: {e}")
            return False
    
    def _solve_math_captcha(self):
        try:
            captcha_text_element = self.browser.find_element('css', '.captcha-text, .math-captcha')
            if not captcha_text_element:
                return False
            
            captcha_text = captcha_text_element.text
            if not captcha_text:
                return False
            
            math_result = self.captcha_solver.solve_captcha(captcha_text, "math")
            if not math_result:
                return False
            
            captcha_input = self.browser.find_element('css', 'input[name*="captcha"], .captcha input')
            if not captcha_input:
                return False
            
            if not self.browser.type_text('css', captcha_input.get_attribute('name'), math_result):
                return False
            
            logger.info(f"Math CAPTCHA solved: {captcha_text} = {math_result}")
            return True
            
        except Exception as e:
            logger.error(f"Error solving math CAPTCHA: {e}")
            return False
    
    def _verify_login_success(self, success_indicators):
        try:
            if not success_indicators:
                success_indicators = ['logout', 'profile', 'dashboard', 'welcome']
            
            page_source = self.browser.get_page_source()
            if not page_source:
                return False
            
            page_lower = page_source.lower()
            for indicator in success_indicators:
                if indicator.lower() in page_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying login success: {e}")
            return False
    
    def submit_form(self, website, form_config, form_data):
        try:
            if not self.browser:
                logger.error("Browser not started")
                return False
            
            if not self.browser.navigate_to(form_config['form_url']):
                return False
            
            self.browser.wait_for_page_load()
            
            if not self._fill_form_fields(form_config['fields'], form_data):
                return False
            
            if self._handle_captcha_if_present():
                logger.info("CAPTCHA handled during form submission")
            
            if not self._submit_form(form_config['submit_button']):
                return False
            
            if self._verify_form_submission_success(form_config.get('success_indicators', [])):
                logger.info(f"Form submitted successfully to {website}")
                self.credential_manager.log_automation(website, "form_submission", "success")
                return True
            else:
                logger.error(f"Form submission failed for {website}")
                self.credential_manager.log_automation(website, "form_submission", "failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during form submission: {e}")
            self.credential_manager.log_automation(website, "form_submission", "error", str(e))
            return False
    
    def _fill_form_fields(self, fields_config, form_data):
        try:
            for field_name, field_config in fields_config.items():
                if field_name not in form_data:
                    continue
                
                selector = field_config.get('selector', f'input[name="{field_name}"]')
                field_type = field_config.get('type', 'text')
                field_by = field_config.get('by', 'css')
                
                if field_type == 'text':
                    if not self.browser.type_text(field_by, selector, form_data[field_name]):
                        logger.warning(f"Failed to fill field: {field_name}")
                        continue
                elif field_type == 'select':
                    if not self._select_option(field_by, selector, form_data[field_name]):
                        logger.warning(f"Failed to select option for field: {field_name}")
                        continue
                elif field_type == 'checkbox':
                    if form_data[field_name]:
                        if not self.browser.click_element(field_by, selector):
                            logger.warning(f"Failed to check checkbox: {field_name}")
                            continue
                
                time.sleep(config.SECURITY_DELAY_MIN)
            
            return True
            
        except Exception as e:
            logger.error(f"Error filling form fields: {e}")
            return False
    
    def _select_option(self, by, selector, value):
        try:
            select_element = self.browser.find_element(by, selector)
            if not select_element:
                return False
            
            from selenium.webdriver.support.ui import Select
            select = Select(select_element)
            select.select_by_visible_text(value)
            return True
            
        except Exception as e:
            logger.error(f"Error selecting option: {e}")
            return False
    
    def _submit_form(self, submit_config):
        try:
            selector = submit_config.get('selector', 'input[type="submit"], button[type="submit"]')
            submit_by = submit_config.get('by', 'css')
            
            if not self.browser.click_element(submit_by, selector):
                logger.error("Failed to submit form")
                return False
            
            time.sleep(config.SECURITY_DELAY_MIN)
            return True
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False
    
    def _verify_form_submission_success(self, success_indicators):
        try:
            if not success_indicators:
                success_indicators = ['success', 'thank you', 'submitted', 'received']
            
            page_source = self.browser.get_page_source()
            if not page_source:
                return False
            
            page_lower = page_source.lower()
            for indicator in success_indicators:
                if indicator.lower() in page_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying form submission: {e}")
            return False
    
    def batch_process(self, websites, process_type="login"):
        try:
            results = []
            
            for website_config in websites:
                website = website_config['website']
                username = website_config['username']
                
                logger.info(f"Processing {website} for {username}")
                
                if process_type == "login":
                    success = self.login_to_website(website, username, website_config['login_config'])
                elif process_type == "form_submission":
                    success = self.submit_form(website, website_config['form_config'], website_config['form_data'])
                else:
                    logger.warning(f"Unknown process type: {process_type}")
                    continue
                
                results.append({
                    'website': website,
                    'username': username,
                    'success': success,
                    'timestamp': time.time()
                })
                
                time.sleep(config.SECURITY_DELAY_MAX)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during batch processing: {e}")
            return []
    
    def get_automation_status(self):
        try:
            status = {
                'browser_running': self.browser is not None,
                'current_website': self.current_website,
                'automation_active': self.browser and self.browser.driver is not None
            }
            
            if self.browser and self.browser.driver:
                status.update({
                    'current_url': self.browser.get_current_url(),
                    'page_title': self.browser.get_page_title(),
                    'window_size': self.browser.get_window_size()
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting automation status: {e}")
            return {}
    
    def take_screenshot(self, filename=None):
        try:
            if not self.browser:
                logger.error("Browser not started")
                return None
            
            return self.browser.take_screenshot(filename)
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def save_form_template(self, website, template_name, form_data):
        try:
            return self.credential_manager.save_form_template(website, template_name, form_data)
        except Exception as e:
            logger.error(f"Error saving form template: {e}")
            return False
    
    def get_form_template(self, website, template_name):
        try:
            return self.credential_manager.get_form_template(website, template_name)
        except Exception as e:
            logger.error(f"Error getting form template: {e}")
            return None
    
    def get_automation_logs(self, limit=100):
        try:
            return self.credential_manager.get_automation_logs(limit)
        except Exception as e:
            logger.error(f"Error getting automation logs: {e}")
            return []


