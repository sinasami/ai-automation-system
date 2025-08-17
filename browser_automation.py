import time
import logging
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import config

logger = logging.getLogger(__name__)

class BrowserAutomation:
    def __init__(self, browser_type=None, headless=False):
        self.browser_type = browser_type or config.BROWSER_TYPE
        self.headless = headless or config.HEADLESS
        self.driver = None
        self.wait = None
    
    def start_browser(self):
        try:
            if self.browser_type.lower() == "chrome":
                self.driver = self._setup_chrome()
            elif self.browser_type.lower() == "firefox":
                self.driver = self._setup_firefox()
            elif self.browser_type.lower() == "edge":
                self.driver = self._setup_edge()
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
            
            self.driver.implicitly_wait(config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            self.wait = WebDriverWait(self.driver, config.IMPLICIT_WAIT)
            
            logger.info(f"Started {self.browser_type} browser successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False
    
    def _setup_chrome(self):
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        if platform.system() == "Windows":
            if platform.machine().endswith('64'):
                service = Service(ChromeDriverManager(os_type="win64").install())
            else:
                service = Service(ChromeDriverManager(os_type="win32").install())
        else:
            service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _setup_firefox(self):
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=firefox_options)
    
    def _setup_edge(self):
        edge_options = EdgeOptions()
        if self.headless:
            edge_options.add_argument("--headless")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--window-size=1920,1080")
        
        service = Service(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=edge_options)
    
    def close_browser(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate_to(self, url):
        try:
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def find_element(self, by, value, timeout=None):
        try:
            wait_time = timeout or config.IMPLICIT_WAIT
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {by}={value}: {e}")
            return None
    
    def find_elements(self, by, value, timeout=None):
        try:
            wait_time = timeout or config.IMPLICIT_WAIT
            elements = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except TimeoutException:
            logger.warning(f"Elements not found: {by}={value}")
            return None
        except Exception as e:
            logger.error(f"Error finding elements {by}={value}: {e}")
            return None
    
    def click_element(self, by, value, timeout=None):
        try:
            element = self.find_element(by, value, timeout)
            if element:
                element.click()
                logger.info(f"Clicked element: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clicking element {by}={value}: {e}")
            return False
    
    def type_text(self, by, value, text, clear_first=True, timeout=None):
        try:
            element = self.find_element(by, value, timeout)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                logger.info(f"Typed text into {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error typing text into {by}={value}: {e}")
            return False
    
    def submit_form(self, by, value, timeout=None):
        try:
            element = self.find_element(by, value, timeout)
            if element:
                element.submit()
                logger.info(f"Submitted form: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error submitting form {by}={value}: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=None):
        try:
            wait_time = timeout or config.IMPLICIT_WAIT
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {by}={value}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element {by}={value}: {e}")
            return None
    
    def wait_for_page_load(self, timeout=None):
        try:
            wait_time = timeout or config.PAGE_LOAD_TIMEOUT
            WebDriverWait(self.driver, wait_time).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info("Page loaded completely")
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")
            return False
    
    def take_screenshot(self, filename=None):
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            filepath = config.SCREENSHOTS_DIR / filename
            self.driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def get_page_title(self):
        try:
            return self.driver.title
        except Exception as e:
            logger.error(f"Error getting page title: {e}")
            return None
    
    def get_current_url(self):
        try:
            return self.driver.current_url
        except Exception as e:
            logger.error(f"Error getting current URL: {e}")
            return None
    
    def execute_script(self, script):
        try:
            result = self.driver.execute_script(script)
            logger.info(f"Executed script: {script[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return None
    
    def switch_to_frame(self, frame_reference):
        try:
            self.driver.switch_to.frame(frame_reference)
            logger.info(f"Switched to frame: {frame_reference}")
            return True
        except Exception as e:
            logger.error(f"Error switching to frame: {e}")
            return False
    
    def switch_to_default_content(self):
        try:
            self.driver.switch_to.default_content()
            logger.info("Switched to default content")
            return True
        except Exception as e:
            logger.error(f"Error switching to default content: {e}")
            return False
    
    def get_cookies(self):
        try:
            return self.driver.get_cookies()
        except Exception as e:
            logger.error(f"Error getting cookies: {e}")
            return []
    
    def add_cookie(self, cookie_dict):
        try:
            self.driver.add_cookie(cookie_dict)
            logger.info(f"Added cookie: {cookie_dict.get('name', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error adding cookie: {e}")
            return False
    
    def delete_all_cookies(self):
        try:
            self.driver.delete_all_cookies()
            logger.info("Deleted all cookies")
            return True
        except Exception as e:
            logger.error(f"Error deleting cookies: {e}")
            return False
    
    def refresh_page(self):
        try:
            self.driver.refresh()
            logger.info("Page refreshed")
            return True
        except Exception as e:
            logger.error(f"Error refreshing page: {e}")
            return False
    
    def go_back(self):
        try:
            self.driver.back()
            logger.info("Went back to previous page")
            return True
        except Exception as e:
            logger.error(f"Error going back: {e}")
            return False
    
    def go_forward(self):
        try:
            self.driver.forward()
            logger.info("Went forward to next page")
            return True
        except Exception as e:
            logger.error(f"Error going forward: {e}")
            return False
    
    def maximize_window(self):
        try:
            self.driver.maximize_window()
            logger.info("Window maximized")
            return True
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return False
    
    def set_window_size(self, width, height):
        try:
            self.driver.set_window_size(width, height)
            logger.info(f"Window size set to {width}x{height}")
            return True
        except Exception as e:
            logger.error(f"Error setting window size: {e}")
            return False
    
    def get_window_size(self):
        try:
            return self.driver.get_window_size()
        except Exception as e:
            logger.error(f"Error getting window size: {e}")
            return None
    
    def is_element_present(self, by, value, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element is not None
        except TimeoutException:
            return False
        except Exception as e:
            logger.error(f"Error checking element presence: {e}")
            return False
    
    def is_element_visible(self, by, value, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element.is_displayed()
        except TimeoutException:
            return False
        except Exception as e:
            logger.error(f"Error checking element visibility: {e}")
            return False
    
    def wait_for_element_clickable(self, by, value, timeout=None):
        try:
            wait_time = timeout or config.IMPLICIT_WAIT
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not clickable: {by}={value}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for clickable element: {e}")
            return None
    
    def scroll_to_element(self, by, value, timeout=None):
        try:
            element = self.find_element(by, value, timeout)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                logger.info(f"Scrolled to element: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error scrolling to element: {e}")
            return False
    
    def scroll_to_bottom(self):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.info("Scrolled to bottom of page")
            return True
        except Exception as e:
            logger.error(f"Error scrolling to bottom: {e}")
            return False
    
    def scroll_to_top(self):
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.info("Scrolled to top of page")
            return True
        except Exception as e:
            logger.error(f"Error scrolling to top: {e}")
            return False
    
    def get_page_source(self):
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error getting page source: {e}")
            return None
    
    def accept_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            logger.info("Alert accepted")
            return True
        except Exception as e:
            logger.error(f"Error accepting alert: {e}")
            return False
    
    def dismiss_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            logger.info("Alert dismissed")
            return True
        except Exception as e:
            logger.error(f"Error dismissing alert: {e}")
            return False
    
    def get_alert_text(self):
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            logger.info(f"Alert text: {text}")
            return text
        except Exception as e:
            logger.error(f"Error getting alert text: {e}")
            return None
    
    def send_keys_to_alert(self, text):
        try:
            alert = self.driver.switch_to.alert
            alert.send_keys(text)
            logger.info(f"Sent keys to alert: {text}")
            return True
        except Exception as e:
            logger.error(f"Error sending keys to alert: {e}")
            return False

