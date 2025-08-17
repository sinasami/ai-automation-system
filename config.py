import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
TEMPLATES_DIR = BASE_DIR / "templates"

BROWSER_TYPE = "chrome"
HEADLESS = False
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30

ENCRYPTION_KEY_FILE = DATA_DIR / "encryption_key.key"
DATABASE_FILE = DATA_DIR / "credentials.db"

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "automation.log"

CAPTCHA_TIMEOUT = 30
CAPTCHA_RETRY_ATTEMPTS = 3

SECURITY_DELAY_MIN = 1
SECURITY_DELAY_MAX = 3

for directory in [DATA_DIR, LOGS_DIR, SCREENSHOTS_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)


